"""
Odoo MCP Server - Accounting integration via Odoo 19+ JSON-RPC API

Requirements:
    pip install xmlrpc2

Usage:
    python -m mcp.odoo.server
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.base import BaseMCPServer, MCPTool


class OdooMCPServer(BaseMCPServer):
    """MCP server for Odoo ERP operations."""

    def __init__(self, config: dict = None):
        super().__init__("odoo", config)

        # Load configuration from environment
        self.url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.db = os.getenv('ODOO_DB', 'odoo')
        self.username = os.getenv('ODOO_USERNAME', 'admin')
        self.api_key = os.getenv('ODOO_API_KEY', '')
        self.uid = None
        self.models = None

    def _connect(self):
        """Connect to Odoo via JSON-RPC."""
        if self.uid:
            return True

        try:
            import xmlrpc.client as xmlrpclib

            # Get server version (to determine if JSON-RPC or XML-RPC)
            common = xmlrpclib.ServerProxy(f'{self.url}/jsonrpc')

            # Authenticate
            self.uid = common.authenticate(self.db, self.username, self.api_key, {})

            if self.uid:
                self.models = xmlrpclib.ServerProxy(f'{self.url}/jsonrpc')
                self.logger.info(f"Connected to Odoo: {self.url}")
                return True
            else:
                self.logger.error("Authentication failed")
                return False

        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False

    def get_tools(self):
        """Return available tools."""
        return [
            MCPTool(
                name="get_invoices",
                description="Get invoices from Odoo",
                input_schema={
                    "type": "object",
                    "properties": {
                        "state": {"type": "string", "description": "Filter by state (draft, open, paid)"},
                        "limit": {"type": "integer", "default": 10}
                    }
                }
            ),
            MCPTool(
                name="create_invoice",
                description="Create a draft invoice",
                input_schema={
                    "type": "object",
                    "properties": {
                        "partner_id": {"type": "integer", "description": "Partner/Customer ID"},
                        "invoice_date": {"type": "string", "description": "Invoice date (YYYY-MM-DD)"},
                        "lines": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "price_unit": {"type": "number"},
                                    "account_id": {"type": "integer"}
                                }
                            },
                            "description": "Invoice lines"
                        }
                    },
                    "required": ["partner_id", "lines"]
                }
            ),
            MCPTool(
                name="get_contacts",
                description="Get customers/suppliers from Odoo",
                input_schema={
                    "type": "object",
                    "properties": {
                        "partner_type": {"type": "string", "description": "customer, supplier, or leave empty for all"},
                        "limit": {"type": "integer", "default": 20}
                    }
                }
            ),
            MCPTool(
                name="get_account_balance",
                description="Get account balance summary",
                input_schema={
                    "type": "object",
                    "properties": {
                        "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                        "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                    }
                }
            ),
            MCPTool(
                name="get_products",
                description="Get products from Odoo",
                input_schema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 20}
                    }
                }
            )
        ]

    def handle_request(self, method: str, params: dict = None):
        """Handle MCP request."""
        params = params or {}

        # Check for list_tools before requiring connection
        if method == "list_tools":
            return [t.to_dict() for t in self.get_tools()]

        # For other methods, ensure we're connected
        if not self._connect():
            return {"error": "Not connected to Odoo. Check ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_API_KEY"}

        if method == "get_invoices":
            return self.get_invoices(params)
        elif method == "create_invoice":
            return self.create_invoice(params)
        elif method == "get_contacts":
            return self.get_contacts(params)
        elif method == "get_account_balance":
            return self.get_account_balance(params)
        elif method == "get_products":
            return self.get_products(params)
        else:
            return {"error": f"Unknown method: {method}"}

    def get_invoices(self, params: dict) -> dict:
        """Get invoices from Odoo."""
        try:
            domain = []
            if params.get('state'):
                domain.append(('state', '=', params['state']))
            limit = params.get('limit', 10)

            # Use xmlrpc to fetch invoices
            import xmlrpc.client as xmlrpclib
            models = xmlrpclib.ServerProxy(f'{self.url}/jsonrpc')

            invoice_ids = models.execute_kw(
                self.db, self.uid, self.api_key,
                'account.move',
                'search_read',
                [domain],
                {'limit': limit, 'fields': ['name', 'partner_id', 'invoice_date', 'amount_total', 'state', 'invoice_origin']}
            )

            return {"invoices": invoice_ids, "count": len(invoice_ids)}

        except Exception as e:
            self.logger.error(f"Error getting invoices: {e}")
            return {"error": str(e)}

    def create_invoice(self, params: dict) -> dict:
        """Create a draft invoice."""
        try:
            import xmlrpc.client as xmlrpclib
            models = xmlrpclib.ServerProxy(f'{self.url}/jsonrpc')

            partner_id = params['partner_id']
            invoice_date = params.get('invoice_date', str(date.today()))
            lines = params.get('lines', [])

            # Create invoice
            invoice_data = {
                'partner_id': partner_id,
                'invoice_date': invoice_date,
                'move_type': 'out_invoice',
            }

            invoice_id = models.execute_kw(
                self.db, self.uid, self.api_key,
                'account.move',
                'create',
                [invoice_data]
            )

            # Add invoice lines
            for line in lines:
                line_data = {
                    'move_id': invoice_id,
                    'name': line.get('name', 'Product'),
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', 0),
                }
                if line.get('account_id'):
                    line_data['account_id'] = line['account_id']

                models.execute_kw(
                    self.db, self.uid, self.api_key,
                    'account.move.line',
                    'create',
                    [line_data]
                )

            return {"status": "success", "invoice_id": invoice_id}

        except Exception as e:
            self.logger.error(f"Error creating invoice: {e}")
            return {"error": str(e)}

    def get_contacts(self, params: dict) -> dict:
        """Get contacts from Odoo."""
        try:
            import xmlrpc.client as xmlrpclib
            models = xmlrpclib.ServerProxy(f'{self.url}/jsonrpc')

            domain = []
            if params.get('partner_type') == 'customer':
                domain.append(('customer_rank', '>', 0))
            elif params.get('partner_type') == 'supplier':
                domain.append(('supplier_rank', '>', 0))

            limit = params.get('limit', 20)

            contact_ids = models.execute_kw(
                self.db, self.uid, self.api_key,
                'res.partner',
                'search_read',
                [domain],
                {'limit': limit, 'fields': ['id', 'name', 'email', 'phone', 'customer_rank', 'supplier_rank']}
            )

            return {"contacts": contact_ids, "count": len(contact_ids)}

        except Exception as e:
            self.logger.error(f"Error getting contacts: {e}")
            return {"error": str(e)}

    def get_account_balance(self, params: dict) -> dict:
        """Get account balance summary."""
        try:
            import xmlrpc.client as xmlrpclib
            from datetime import date, timedelta

            models = xmlrpclib.ServerProxy(f'{self.url}/jsonrpc')

            date_from = params.get('date_from', str(date.today() - timedelta(days=30)))
            date_to = params.get('date_to', str(date.today()))

            # Get account move lines
            domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('move_id.state', '=', 'posted')
            ]

            move_lines = models.execute_kw(
                self.db, self.uid, self.api_key,
                'account.move.line',
                'search_read',
                [domain],
                {'fields': ['account_id', 'debit', 'credit', 'date', 'partner_id', 'name']}
            )

            # Aggregate by account
            balances = {}
            for line in move_lines:
                account_id = line.get('account_id', [(0, 'Unknown')])[0]
                account_name = line.get('account_id', [(0, 'Unknown')])[1]

                if account_id not in balances:
                    balances[account_id] = {'name': account_name, 'debit': 0, 'credit': 0}

                balances[account_id]['debit'] += line.get('debit', 0)
                balances[account_id]['credit'] += line.get('credit', 0)

            return {
                "date_from": date_from,
                "date_to": date_to,
                "accounts": balances,
                "total_debit": sum(a['debit'] for a in balances.values()),
                "total_credit": sum(a['credit'] for a in balances.values())
            }

        except Exception as e:
            self.logger.error(f"Error getting account balance: {e}")
            return {"error": str(e)}

    def get_products(self, params: dict) -> dict:
        """Get products from Odoo."""
        try:
            import xmlrpc.client as xmlrpclib
            models = xmlrpclib.ServerProxy(f'{self.url}/jsonrpc')

            limit = params.get('limit', 20)

            product_ids = models.execute_kw(
                self.db, self.uid, self.api_key,
                'product.product',
                'search_read',
                [[('type', '=', 'service')]],
                {'limit': limit, 'fields': ['id', 'name', 'list_price', 'standard_price', 'default_code']}
            )

            return {"products": product_ids, "count": len(product_ids)}

        except Exception as e:
            self.logger.error(f"Error getting products: {e}")
            return {"error": str(e)}


def main():
    """Main entry point."""
    server = OdooMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
