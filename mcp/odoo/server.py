#!/usr/bin/env python3
"""
Odoo Accounting MCP Server for Personal AI Employee (Gold Tier)

Provides full accounting integration with Odoo Community Edition via JSON-RPC API.
Supports invoices, payments, customers, products, and financial reports.

Configuration:
- ODOO_URL: Odoo server URL (default: http://localhost:8069)
- ODOO_DB: Database name (default: odoo)
- ODOO_USERNAME: Admin username or email
- ODOO_API_KEY: API key (not password - generate in Odoo user settings)
- VAULT_PATH: Path to vault for logging

Run:
    python mcp/odoo/server.py

Odoo Setup:
1. Install Odoo Community Edition (local or cloud)
2. Create database for your business
3. Go to Settings → Users → Your User
4. Generate API Key (not use password)
5. Set environment variables
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("odoo-mcp")

# Create FastMCP server
server = FastMCP(
    "odoo",
    instructions="Odoo Accounting integration for Personal AI Employee (Gold Tier)"
)

# Odoo JSON-RPC endpoints
ODOO_JSONRPC_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'odoo')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_API_KEY = os.getenv('ODOO_API_KEY')

# Session cache for authenticated uid
_cached_uid = None


def get_odoo_credentials() -> Dict[str, str]:
    """Get Odoo credentials from environment or vault."""
    global ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_API_KEY

    # Check vault secrets if not in environment
    if not ODOO_API_KEY:
        vault_path = os.getenv('VAULT_PATH', './vault')
        creds_file = Path(vault_path) / 'secrets' / 'odoo_credentials.json'
        if creds_file.exists():
            creds = json.loads(creds_file.read_text())
            ODOO_URL = creds.get('url', ODOO_URL)
            ODOO_DB = creds.get('db', ODOO_DB)
            ODOO_USERNAME = creds.get('username', ODOO_USERNAME)
            ODOO_API_KEY = creds.get('api_key')

    return {
        'url': ODOO_JSONRPC_URL,
        'db': ODOO_DB,
        'username': ODOO_USERNAME,
        'api_key': ODOO_API_KEY
    }


def is_dry_run() -> bool:
    """Check if dry_run mode is enabled."""
    return os.getenv('DRY_RUN', 'true').lower() == 'true'


def authenticate_odoo() -> int:
    """
    Authenticate with Odoo and return the user ID (uid).
    Uses the /web/session/authenticate endpoint.
    Caches the result for subsequent calls.
    """
    global _cached_uid

    if _cached_uid is not None:
        return _cached_uid

    creds = get_odoo_credentials()

    if not creds['api_key']:
        raise ValueError("Odoo API key not configured")

    url = f"{creds['url']}/jsonrpc"

    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "login",
            "args": [creds['db'], creds['username'], creds['api_key']]
        },
        "id": 1
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        if 'error' in result:
            error = result['error']
            raise Exception(f"Odoo auth error: {error.get('data', {}).get('message', error)}")

        uid = result.get('result', {}).get('uid')
        if not uid:
            raise Exception(f"Authentication failed: {result}")

        _cached_uid = uid
        logger.info(f"Authenticated with Odoo as uid={uid}")
        return uid

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error authenticating with Odoo: {e}")
        raise


def odoo_jsonrpc_call(model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
    """
    Make a JSON-RPC call to Odoo server using session-based authentication.

    Args:
        model: Odoo model name (e.g., 'account.move', 'res.partner')
        method: Method to call (e.g., 'search_read', 'create')
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Response from Odoo server
    """
    creds = get_odoo_credentials()

    if not creds['api_key']:
        raise ValueError("Odoo API key not configured")

    # Authenticate to get uid
    uid = authenticate_odoo()

    url = f"{creds['url']}/jsonrpc"

    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                creds['db'],
                uid,
                creds['api_key'],
                model,
                method
            ]
        },
        "id": 1
    }

    if args:
        payload["params"]["args"].extend(args)

    if kwargs:
        payload["params"]["args"].append(kwargs)

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()

        if 'error' in result:
            error = result['error']
            logger.error(f"Odoo API error: {error.get('data', {}).get('message', error)}")
            raise Exception(f"Odoo API error: {error}")

        return result.get('result')

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error calling Odoo: {e}")
        raise


@server.tool()
def odoo_status() -> Dict[str, Any]:
    """
    Check Odoo connection status and configuration.
    
    Returns:
        Dict with connection status and capabilities
    """
    creds = get_odoo_credentials()
    
    status = {
        "status": "needs_configuration",
        "configured": bool(creds['api_key']),
        "url": creds['url'],
        "database": creds['db'],
        "username": creds['username'],
        "tier": "gold",
        "capabilities": [
            "create_invoice",
            "list_invoices",
            "create_payment",
            "list_payments",
            "create_customer",
            "list_customers",
            "get_financial_summary",
            "get_account_moves"
        ]
    }
    
    if creds['api_key']:
        try:
            # Test connection by getting current user
            result = odoo_jsonrpc_call('res.users', 'search_read', 
                [[['login', '=', creds['username']]]], 
                {'fields': ['name', 'login'], 'limit': 1}
            )
            
            if result:
                status["status"] = "connected"
                status["user"] = result[0].get('name')
        except Exception as e:
            status["status"] = "connection_error"
            status["error"] = str(e)
    
    return status


@server.tool()
def create_invoice(
    partner_name: str,
    partner_email: str,
    invoice_lines: List[Dict[str, Any]],
    invoice_date: str = None,
    payment_terms: int = 30
) -> Dict[str, Any]:
    """
    Create a new customer invoice in Odoo.

    Args:
        partner_name: Customer name
        partner_email: Customer email
        invoice_lines: List of line items with:
            - name: Description
            - quantity: Quantity (default: 1)
            - price_unit: Unit price
            - account_id: Account ID (optional, uses default income account)
        invoice_date: Invoice date (YYYY-MM-DD, default: today)
        payment_terms: Payment terms in days (default: 30)

    Returns:
        Dict with invoice details including ID and number
    """
    try:
        # Check dry_run mode
        if is_dry_run():
            total = sum(line.get('price_unit', 0) * line.get('quantity', 1) for line in invoice_lines)
            logger.info(f"[DRY RUN] Would create invoice for {partner_name} (${total:.2f})")
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would create invoice for {partner_name} (${total:.2f})",
                "partner": partner_name,
                "partner_email": partner_email,
                "line_count": len(invoice_lines),
                "total": total,
                "payment_terms": payment_terms,
                "note": "Set DRY_RUN=false to actually create invoice"
            }
        # Find or create partner
        partner_result = odoo_jsonrpc_call('res.partner', 'search_read',
            [[['email', '=', partner_email]]],
            {'fields': ['id', 'name', 'email'], 'limit': 1}
        )
        
        if partner_result:
            partner_id = partner_result[0]['id']
            logger.info(f"Found existing partner: {partner_name}")
        else:
            # Create new partner
            partner_id = odoo_jsonrpc_call('res.partner', 'create', [], {
                'name': partner_name,
                'email': partner_email,
                'customer_rank': 1
            })
            logger.info(f"Created new partner: {partner_name}")
        
        # Prepare invoice lines
        line_commands = []
        for line in invoice_lines:
            line_commands.append([0, 0, {
                'name': line.get('name', 'Service'),
                'quantity': line.get('quantity', 1),
                'price_unit': line.get('price_unit', 0),
                'account_id': line.get('account_id')  # Optional
            }])
        
        # Create invoice
        invoice_date = invoice_date or datetime.now().strftime('%Y-%m-%d')
        due_date = (datetime.now() + timedelta(days=payment_terms)).strftime('%Y-%m-%d')
        
        invoice_id = odoo_jsonrpc_call('account.move', 'create', [], {
            'move_type': 'out_invoice',
            'partner_id': partner_id,
            'invoice_date': invoice_date,
            'invoice_date_due': due_date,
            'invoice_line_ids': line_commands,
            'state': 'draft'
        })
        
        # Get invoice number
        invoice_data = odoo_jsonrpc_call('account.move', 'read', 
            [[invoice_id]], 
            {'fields': ['name', 'amount_total', 'state']}
        )
        
        # Log to vault
        _log_invoice_to_vault({
            'id': invoice_id,
            'number': invoice_data[0].get('name', 'Draft'),
            'partner': partner_name,
            'total': invoice_data[0].get('amount_total', 0),
            'state': 'draft',
            'date': invoice_date
        })
        
        return {
            "success": True,
            "invoice_id": invoice_id,
            "invoice_number": invoice_data[0].get('name', 'Draft'),
            "partner": partner_name,
            "partner_id": partner_id,
            "total": invoice_data[0].get('amount_total', 0),
            "state": invoice_data[0].get('state'),
            "due_date": due_date,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def list_invoices(
    partner_email: str = None,
    state: str = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    List invoices from Odoo with optional filtering.
    
    Args:
        partner_email: Filter by customer email (optional)
        state: Filter by state (draft, posted, paid, cancel)
        limit: Maximum number of invoices to return
    
    Returns:
        Dict with list of invoices
    """
    try:
        domain = []
        
        if partner_email:
            # Get partner ID
            partner_result = odoo_jsonrpc_call('res.partner', 'search_read',
                [[['email', '=', partner_email]]],
                {'fields': ['id'], 'limit': 1}
            )
            if partner_result:
                domain.append(['partner_id', '=', partner_result[0]['id']])
        
        if state:
            domain.append(['state', '=', state])
        
        invoices = odoo_jsonrpc_call('account.move', 'search_read',
            domain + [['move_type', '=', 'out_invoice']],
            {
                'fields': ['name', 'partner_id', 'amount_total', 'amount_due', 
                          'invoice_date', 'invoice_date_due', 'state'],
                'limit': limit,
                'order': 'invoice_date desc'
            }
        )
        
        # Format partner_id tuple to name
        for inv in invoices:
            if isinstance(inv.get('partner_id'), tuple):
                inv['partner_id'] = inv['partner_id'][1]
        
        return {
            "success": True,
            "count": len(invoices),
            "invoices": invoices
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def post_invoice(invoice_id: int) -> Dict[str, Any]:
    """
    Confirm and post a draft invoice in Odoo (makes it visible to customer).

    Args:
        invoice_id: Odoo invoice ID (must be in 'draft' state)

    Returns:
        Dict with invoice posting result
    """
    try:
        if is_dry_run():
            logger.info(f"[DRY RUN] Would post invoice {invoice_id}")
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would post invoice {invoice_id}",
                "invoice_id": invoice_id,
                "note": "Set DRY_RUN=false to actually post"
            }

        # Get invoice current state
        invoice_data = odoo_jsonrpc_call('account.move', 'read',
            [[invoice_id]],
            {'fields': ['name', 'state']}
        )

        if not invoice_data:
            return {
                "success": False,
                "error": f"Invoice {invoice_id} not found"
            }

        if invoice_data[0].get('state') == 'posted':
            return {
                "success": False,
                "error": "Invoice already posted",
                "invoice_id": invoice_id,
                "invoice_number": invoice_data[0].get('name')
            }

        # Action: post (confirm) the invoice
        odoo_jsonrpc_call('account.move', 'action_post', [[invoice_id]], {})

        # Get updated invoice data
        updated_data = odoo_jsonrpc_call('account.move', 'read',
            [[invoice_id]],
            {'fields': ['name', 'amount_total', 'state', 'invoice_date_due']}
        )

        result = updated_data[0] if updated_data else {}

        _log_invoice_to_vault({
            'id': invoice_id,
            'number': result.get('name', 'Draft'),
            'total': result.get('amount_total', 0),
            'state': result.get('state', 'posted'),
            'date': result.get('invoice_date_due'),
            'action': 'posted'
        })

        return {
            "success": True,
            "invoice_id": invoice_id,
            "invoice_number": result.get('name'),
            "total": result.get('amount_total', 0),
            "state": result.get('state'),
            "due_date": result.get('invoice_date_due'),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error posting invoice: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def create_payment(
    invoice_id: int,
    amount: float,
    payment_date: str = None,
    payment_reference: str = None
) -> Dict[str, Any]:
    """
    Register a payment for an invoice.
    
    Args:
        invoice_id: Odoo invoice ID
        amount: Payment amount
        payment_date: Payment date (YYYY-MM-DD, default: today)
        payment_reference: Payment reference/narration
    
    Returns:
        Dict with payment details
    """
    try:
        if is_dry_run():
            logger.info(f"[DRY RUN] Would create payment of ${amount:.2f} for invoice {invoice_id}")
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would create payment of ${amount:.2f} for invoice {invoice_id}",
                "invoice_id": invoice_id,
                "amount": amount,
                "payment_date": payment_date or datetime.now().strftime('%Y-%m-%d'),
                "note": "Set DRY_RUN=false to actually create"
            }

        payment_date = payment_date or datetime.now().strftime('%Y-%m-%d')
        
        # Create payment wizard
        payment_result = odoo_jsonrpc_call('account.payment.register', 'create', [], {
            'payment_date': payment_date,
            'amount': amount,
            'payment_reference': payment_reference or f'Payment for invoice {invoice_id}'
        })
        
        # Create payment
        odoo_jsonrpc_call('account.payment.register', 'create_payments', 
            [[payment_result]], {})
        
        # Get updated invoice state
        invoice_data = odoo_jsonrpc_call('account.move', 'read',
            [[invoice_id]],
            {'fields': ['name', 'amount_total', 'amount_due', 'state']}
        )
        
        return {
            "success": True,
            "invoice_id": invoice_id,
            "invoice_number": invoice_data[0].get('name'),
            "payment_amount": amount,
            "payment_date": payment_date,
            "remaining_due": invoice_data[0].get('amount_due', 0),
            "invoice_state": invoice_data[0].get('state'),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def list_payments(limit: int = 10) -> Dict[str, Any]:
    """
    List recent payments.
    
    Args:
        limit: Maximum number of payments to return
    
    Returns:
        Dict with list of payments
    """
    try:
        payments = odoo_jsonrpc_call('account.payment', 'search_read',
            [],
            {
                'fields': ['name', 'partner_id', 'amount', 'payment_date', 
                          'state', 'payment_reference'],
                'limit': limit,
                'order': 'payment_date desc'
            }
        )
        
        # Format partner_id tuple to name
        for pmt in payments:
            if isinstance(pmt.get('partner_id'), tuple):
                pmt['partner_id'] = pmt['partner_id'][1]
        
        return {
            "success": True,
            "count": len(payments),
            "payments": payments
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def create_customer(
    name: str,
    email: str,
    phone: str = None,
    company_name: str = None
) -> Dict[str, Any]:
    """
    Create a new customer in Odoo.
    
    Args:
        name: Customer name
        email: Email address
        phone: Phone number (optional)
        company_name: Company name (optional)
    
    Returns:
        Dict with customer details
    """
    try:
        if is_dry_run():
            logger.info(f"[DRY RUN] Would create customer: {name} ({email})")
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would create customer: {name}",
                "name": name,
                "email": email,
                "phone": phone,
                "company_name": company_name,
                "note": "Set DRY_RUN=false to actually create"
            }

        # Check if customer exists
        existing = odoo_jsonrpc_call('res.partner', 'search_read',
            [[['email', '=', email]]],
            {'fields': ['id', 'name'], 'limit': 1}
        )
        
        if existing:
            return {
                "success": False,
                "error": "Customer already exists",
                "customer_id": existing[0]['id'],
                "name": existing[0]['name']
            }
        
        # Create customer
        customer_id = odoo_jsonrpc_call('res.partner', 'create', [], {
            'name': name,
            'email': email,
            'phone': phone,
            'company_name': company_name,
            'customer_rank': 1
        })
        
        return {
            "success": True,
            "customer_id": customer_id,
            "name": name,
            "email": email,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def list_customers(limit: int = 20) -> Dict[str, Any]:
    """
    List customers from Odoo.
    
    Args:
        limit: Maximum number of customers to return
    
    Returns:
        Dict with list of customers
    """
    try:
        customers = odoo_jsonrpc_call('res.partner', 'search_read',
            [['customer_rank', '>', 0]],
            {
                'fields': ['name', 'email', 'phone', 'company_name'],
                'limit': limit,
                'order': 'name'
            }
        )
        
        return {
            "success": True,
            "count": len(customers),
            "customers": customers
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def get_financial_summary(
    period_days: int = 30
) -> Dict[str, Any]:
    """
    Get financial summary for the specified period.
    
    Args:
        period_days: Number of days to summarize (default: 30)
    
    Returns:
        Dict with revenue, expenses, invoices, and payments summary
    """
    try:
        cutoff_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
        
        # Get invoices in period
        invoices = odoo_jsonrpc_call('account.move', 'search_read',
            [
                ['move_type', '=', 'out_invoice'],
                ['invoice_date', '>=', cutoff_date]
            ],
            {'fields': ['amount_total', 'state']}
        )
        
        # Calculate revenue
        total_revenue = sum(inv['amount_total'] for inv in invoices if inv['state'] == 'posted')
        draft_revenue = sum(inv['amount_total'] for inv in invoices if inv['state'] == 'draft')
        
        # Get payments in period
        payments = odoo_jsonrpc_call('account.payment', 'search_read',
            [['payment_date', '>=', cutoff_date]],
            {'fields': ['amount', 'state']}
        )
        
        total_received = sum(pmt['amount'] for pmt in payments if pmt['state'] == 'posted')
        
        # Get bills (expenses)
        bills = odoo_jsonrpc_call('account.move', 'search_read',
            [
                ['move_type', 'in', ['in_invoice', 'in_refund']],
                ['invoice_date', '>=', cutoff_date]
            ],
            {'fields': ['amount_total', 'state']}
        )
        
        total_expenses = sum(bill['amount_total'] for bill in bills if bill['state'] == 'posted')
        
        return {
            "success": True,
            "period_days": period_days,
            "cutoff_date": cutoff_date,
            "revenue": {
                "total": total_revenue,
                "draft": draft_revenue,
                "invoice_count": len(invoices)
            },
            "expenses": {
                "total": total_expenses,
                "bill_count": len(bills)
            },
            "payments": {
                "total_received": total_received,
                "payment_count": len(payments)
            },
            "profit": total_revenue - total_expenses,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@server.tool()
def get_account_moves(
    account_type: str = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Get account moves (journal entries).
    
    Args:
        account_type: Filter by account type (optional)
        limit: Maximum number of moves to return
    
    Returns:
        Dict with account moves
    """
    try:
        domain = []
        if account_type:
            domain.append(['account_id.account_type', '=', account_type])
        
        moves = odoo_jsonrpc_call('account.move.line', 'search_read',
            domain,
            {
                'fields': ['date', 'name', 'account_id', 'debit', 'credit', 
                          'balance', 'move_id'],
                'limit': limit,
                'order': 'date desc'
            }
        )
        
        # Format tuples
        for move in moves:
            if isinstance(move.get('account_id'), tuple):
                move['account_id'] = move['account_id'][1]
            if isinstance(move.get('move_id'), tuple):
                move['move_id'] = move['move_id'][1]
        
        return {
            "success": True,
            "count": len(moves),
            "moves": moves
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _log_invoice_to_vault(invoice_data: Dict):
    """Log invoice creation to vault for audit trail."""
    try:
        vault_path = os.getenv('VAULT_PATH', './vault')
        logs_dir = Path(vault_path) / 'Logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = logs_dir / f"odoo_invoices_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "invoice_created",
            "data": invoice_data
        }
        
        if log_file.exists():
            logs = json.loads(log_file.read_text())
            if not isinstance(logs, list):
                logs = [logs]
            logs.append(log_entry)
        else:
            logs = [log_entry]
        
        log_file.write_text(json.dumps(logs, indent=2))
        
    except Exception as e:
        logger.warning(f"Failed to log invoice to vault: {e}")


if __name__ == "__main__":
    logger.info("Starting Odoo MCP Server...")
    
    # Test connection
    status = odoo_status()
    logger.info(f"Odoo Status: {status['status']}")
    
    server.run()
