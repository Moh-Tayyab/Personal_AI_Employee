#!/usr/bin/env python3
"""
Accounting Specialist Agent - Gold Tier

This agent handles all accounting operations via Odoo ERP:
- Process invoices and expenses
- Create and validate invoices
- Manage contacts (customers/vendors)
- Generate financial reports
- Handle approval workflow for high-value transactions
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vault/Logs/accounting_specialist.log')
    ]
)
logger = logging.getLogger("AccountingSpecialist")


class AccountingSpecialistAgent:
    """Specialized agent for accounting operations via Odoo."""

    def __init__(self, vault_path: str, dry_run: bool = True):
        self.vault_path = Path(vault_path).resolve()
        self.dry_run = dry_run
        
        # Vault directories
        self.needs_action = self.vault_path / "Needs_Action"
        self.accounting_dir = self.needs_action / "accounting"
        self.drafts = self.vault_path / "Drafts" / "Accounting"
        self.pending_approval = self.vault_path / "Pending_Approval" / "Accounting"
        self.approved = self.vault_path / "Approved" / "Accounting"
        self.done = self.vault_path / "Done" / "Accounting"
        self.logs = self.vault_path / "Logs"
        self.accounting_vault = self.vault_path / "Accounting"
        
        # Ensure directories exist
        for dir_path in [self.accounting_dir, self.drafts, self.pending_approval, 
                         self.approved, self.done, self.logs, self.accounting_vault]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Approval thresholds
        self.approval_threshold = 500.0  # Amount requiring approval
        self.auto_validate_threshold = 100.0  # Amount for auto-validation
        
        # Odoo configuration
        self.odoo_config = {
            "url": "http://localhost:8069",
            "db": "odoo_db",
            "username": "admin",
            "api_key": ""
        }
        
        # Load Odoo config from .env if available
        self._load_odoo_config()
        
        logger.info(f"Accounting Specialist initialized - Vault: {self.vault_path}")
        logger.info(f"Dry run mode: {self.dry_run}")
        logger.info(f"Approval threshold: ${self.approval_threshold}")

    def _load_odoo_config(self):
        """Load Odoo configuration from .env file."""
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text()
            for line in content.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip().upper()
                    value = value.strip()
                    
                    if key == "ODOO_URL":
                        self.odoo_config["url"] = value
                    elif key == "ODOO_DB":
                        self.odoo_config["db"] = value
                    elif key == "ODOO_USERNAME":
                        self.odoo_config["username"] = value
                    elif key == "ODOO_API_KEY":
                        self.odoo_config["api_key"] = value

    def parse_invoice_file(self, file_path: Path) -> Dict:
        """Parse an invoice/expense markdown file."""
        content = file_path.read_text(encoding='utf-8')
        
        # Extract frontmatter
        frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        metadata = {}
        body = content
        
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            body = content[frontmatter_match.end():].strip()
        
        # Extract invoice details from body
        invoice_data = self._extract_invoice_details(body)
        
        return {
            "file_path": file_path,
            "metadata": metadata,
            "body": body,
            "content": content,
            "invoice_data": invoice_data
        }

    def _extract_invoice_details(self, body: str) -> Dict:
        """Extract invoice details from text using regex and parsing."""
        invoice_data = {
            "vendor": None,
            "amount": 0.0,
            "date": None,
            "invoice_number": None,
            "line_items": [],
            "category": "general",
            "payment_terms": None
        }
        
        # Try to extract amount (look for $ or USD patterns)
        amount_patterns = [
            r'\$([\d,]+\.?\d*)',
            r'(\d+\.?\d*)\s*USD',
            r'Total[:\s]*\$?([\d,]+\.?\d*)',
            r'Amount[:\s]*\$?([\d,]+\.?\d*)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    invoice_data["amount"] = float(amount_str)
                except:
                    pass
                break
        
        # Try to extract vendor name
        vendor_patterns = [
            r'Vendor[:\s]*([^\n]+)',
            r'From[:\s]*([^\n]+)',
            r'Company[:\s]*([^\n]+)',
            r'Supplier[:\s]*([^\n]+)'
        ]
        
        for pattern in vendor_patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                invoice_data["vendor"] = match.group(1).strip()
                break
        
        # Try to extract date
        date_patterns = [
            r'Date[:\s]*(\d{4}-\d{2}-\d{2})',
            r'Invoice Date[:\s]*(\d{4}-\d{2}-\d{2})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, body)
            if match:
                invoice_data["date"] = match.group(1)
                break
        
        # Try to extract invoice number
        invoice_num_patterns = [
            r'Invoice[#\s:]*([A-Z0-9-]+)',
            r'Invoice Number[:\s]*([A-Z0-9-]+)',
            r'Inv[\s#]*([A-Z0-9-]+)'
        ]
        
        for pattern in invoice_num_patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                invoice_data["invoice_number"] = match.group(1).strip()
                break
        
        # Categorize based on content
        body_lower = body.lower()
        if "cloud" in body_lower or "aws" in body_lower or "server" in body_lower:
            invoice_data["category"] = "infrastructure"
        elif "marketing" in body_lower or "ads" in body_lower:
            invoice_data["category"] = "marketing"
        elif "software" in body_lower or "subscription" in body_lower:
            invoice_data["category"] = "software"
        elif "office" in body_lower or "supplies" in body_lower:
            invoice_data["category"] = "office_expenses"
        
        # Extract line items (simple parsing)
        lines = body.split('\n')
        for line in lines:
            if re.search(r'\$[\d,]+\.?\d*', line):
                invoice_data["line_items"].append(line.strip())
        
        return invoice_data

    def check_approval_required(self, invoice_data: Dict) -> Tuple[bool, str]:
        """Check if invoice requires approval."""
        amount = invoice_data.get("amount", 0.0)
        
        if amount > self.approval_threshold:
            return True, f"Amount ${amount} exceeds threshold ${self.approval_threshold}"
        
        # Check for new vendor (not in known vendors)
        # In production, this would check against Odoo contacts
        
        return False, None

    def create_invoice_in_odoo(self, invoice_data: Dict) -> Optional[str]:
        """Create invoice in Odoo ERP."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create invoice in Odoo")
            logger.info(f"[DRY RUN] Vendor: {invoice_data.get('vendor', 'Unknown')}")
            logger.info(f"[DRY RUN] Amount: ${invoice_data.get('amount', 0.0)}")
            return "DRAFT_INV_" + datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            from mcp.odoo.server import OdooMCPServer
            
            server = OdooMCPServer()
            
            # Prepare invoice data for Odoo
            odoo_invoice = {
                "move_type": "in_invoice",
                "partner_name": invoice_data.get("vendor", "Unknown Vendor"),
                "invoice_date": invoice_data.get("date", datetime.now().strftime('%Y-%m-%d')),
                "invoice_line_ids": []
            }
            
            # Add line items
            for item in invoice_data.get("line_items", []):
                # Parse line item (simplified)
                odoo_invoice["invoice_line_ids"].append({
                    "name": item,
                    "quantity": 1,
                    "price_unit": invoice_data.get("amount", 0.0)
                })
            
            # Create invoice
            result = server.create_invoice(odoo_invoice)
            invoice_id = result.get("id") if result else None
            
            logger.info(f"Created invoice in Odoo: {invoice_id}")
            return invoice_id
            
        except Exception as e:
            logger.error(f"Failed to create invoice in Odoo: {e}")
            return None

    def validate_invoice_in_odoo(self, invoice_id: str) -> bool:
        """Validate (confirm) invoice in Odoo."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would validate invoice: {invoice_id}")
            return True
        
        try:
            from mcp.odoo.server import OdooMCPServer
            
            server = OdooMCPServer()
            result = server.validate_invoice({"invoice_id": invoice_id})
            
            logger.info(f"Validated invoice in Odoo: {invoice_id}")
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Failed to validate invoice: {e}")
            return False

    def create_approval_request(self, invoice_data: Dict, file_path: Path) -> Path:
        """Create an approval request for high-value invoice."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_file = self.pending_approval / f"APPROVAL_{timestamp}_{Path(file_path).stem}.md"
        
        approval_content = f"""---
type: accounting_approval
created: {datetime.now().isoformat()}
status: pending
category: invoice_approval
vendor: {invoice_data.get('vendor', 'Unknown')}
amount: {invoice_data.get('amount', 0.0)}
---

# Invoice Approval Request

## Invoice Details

- **Vendor:** {invoice_data.get('vendor', 'Unknown')}
- **Amount:** ${invoice_data.get('amount', 0.0):.2f}
- **Date:** {invoice_data.get('date', 'N/A')}
- **Invoice Number:** {invoice_data.get('invoice_number', 'N/A')}
- **Category:** {invoice_data.get('category', 'general')}

## Reason for Approval

Amount exceeds auto-approval threshold of ${self.approval_threshold}

## Original Invoice

---

{Path(file_path).read_text()}

---

## Action Required

Please review and:
- Move to `../Approved/Accounting/` to validate and pay
- Move to `../Rejected/` to decline
- Add comments for modifications

**File:** {approval_file.name}
"""
        
        approval_file.write_text(approval_content, encoding='utf-8')
        logger.info(f"Created approval request: {approval_file}")
        
        return approval_file

    def process_invoice(self, file_path: Path) -> Dict:
        """Process a single invoice."""
        logger.info(f"Processing invoice: {file_path.name}")
        
        try:
            # Parse invoice
            invoice_file = self.parse_invoice_file(file_path)
            invoice_data = invoice_file["invoice_data"]
            
            logger.info(f"Extracted: Vendor={invoice_data.get('vendor')}, Amount=${invoice_data.get('amount')}")
            
            # Check approval required
            needs_approval, reason = self.check_approval_required(invoice_data)
            
            if needs_approval:
                # Create approval request
                approval_file = self.create_approval_request(invoice_data, file_path)
                
                result = {
                    "status": "pending_approval",
                    "file": str(file_path),
                    "approval_file": str(approval_file),
                    "reason": reason,
                    "amount": invoice_data.get("amount", 0.0)
                }
            else:
                # Process directly
                if self.dry_run:
                    # Create draft in Odoo (simulated)
                    invoice_id = f"DRAFT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    draft_file = self.drafts / f"DRAFT_{file_path.stem}.md"
                    draft_file.write_text(f"""---
invoice_id: {invoice_id}
vendor: {invoice_data.get('vendor')}
amount: {invoice_data.get('amount')}
created: {datetime.now().isoformat()}
status: draft
---

# Draft Invoice Created

**Odoo Invoice ID:** {invoice_id}
**Vendor:** {invoice_data.get('vendor')}
**Amount:** ${invoice_data.get('amount', 0.0):.2f}
**Category:** {invoice_data.get('category')}

Auto-validated (amount <= ${self.auto_validate_threshold})
""", encoding='utf-8')
                    
                    result = {
                        "status": "draft_created",
                        "file": str(file_path),
                        "invoice_id": invoice_id,
                        "amount": invoice_data.get("amount", 0.0)
                    }
                else:
                    # Create in Odoo
                    invoice_id = self.create_invoice_in_odoo(invoice_data)
                    
                    if invoice_id:
                        # Auto-validate if below threshold
                        if invoice_data.get("amount", 0.0) <= self.auto_validate_threshold:
                            validated = self.validate_invoice_in_odoo(invoice_id)
                            
                            if validated:
                                # Move to Done
                                done_file = self.done / file_path.name
                                file_path.rename(done_file)
                                
                                result = {
                                    "status": "validated",
                                    "file": str(file_path),
                                    "invoice_id": invoice_id,
                                    "amount": invoice_data.get("amount", 0.0)
                                }
                            else:
                                result = {
                                    "status": "created",
                                    "file": str(file_path),
                                    "invoice_id": invoice_id,
                                    "amount": invoice_data.get("amount", 0.0)
                                }
                        else:
                            result = {
                                "status": "created",
                                "file": str(file_path),
                                "invoice_id": invoice_id,
                                "amount": invoice_data.get("amount", 0.0)
                            }
                    else:
                        result = {
                            "status": "failed",
                            "file": str(file_path),
                            "error": "Failed to create invoice in Odoo"
                        }
            
            # Log action
            self.log_action(invoice_file, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing invoice {file_path.name}: {e}")
            return {
                "status": "error",
                "file": str(file_path),
                "error": str(e)
            }

    def log_action(self, invoice_file: Dict, result: Dict):
        """Log the accounting action."""
        log_file = self.logs / f"accounting_log_{datetime.now().strftime('%Y%m%d')}.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "invoice": {
                "vendor": invoice_file["invoice_data"].get("vendor", "Unknown"),
                "amount": invoice_file["invoice_data"].get("amount", 0.0),
                "category": invoice_file["invoice_data"].get("category", "general")
            },
            "result": result
        }
        
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except:
                logs = []
        
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

    def process_all_invoices(self) -> List[Dict]:
        """Process all invoices in the needs action folder."""
        results = []
        
        # Find invoice files
        invoice_files = []
        if self.accounting_dir.exists():
            invoice_files.extend(self.accounting_dir.glob("*.md"))
        invoice_files.extend(self.needs_action.glob("INVOICE_*.md"))
        
        logger.info(f"Found {len(invoice_files)} invoice files")
        
        for invoice_file in invoice_files:
            result = self.process_invoice(invoice_file)
            results.append(result)
        
        return results

    def generate_report(self, results: List[Dict]) -> str:
        """Generate a processing report."""
        report = f"""# Accounting Specialist Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Dry Run:** {self.dry_run}
**Approval Threshold:** ${self.approval_threshold}

## Summary

| Status | Count |
|--------|-------|
| Validated | {sum(1 for r in results if r['status'] == 'validated')} |
| Created | {sum(1 for r in results if r['status'] == 'created')} |
| Draft Created | {sum(1 for r in results if r['status'] == 'draft_created')} |
| Pending Approval | {sum(1 for r in results if r['status'] == 'pending_approval')} |
| Failed | {sum(1 for r in results if r['status'] == 'failed')} |

## Financial Summary

"""
        
        total_amount = sum(r.get("amount", 0.0) for r in results)
        pending_amount = sum(r.get("amount", 0.0) for r in results if r["status"] == "pending_approval")
        validated_amount = sum(r.get("amount", 0.0) for r in results if r["status"] == "validated")
        
        report += f"- **Total Amount Processed:** ${total_amount:.2f}\n"
        report += f"- **Pending Approval:** ${pending_amount:.2f}\n"
        report += f"- **Validated:** ${validated_amount:.2f}\n\n"
        
        report += "## Details\n\n"
        
        for result in results:
            report += f"### {Path(result['file']).name}\n"
            report += f"- **Status:** {result['status']}\n"
            report += f"- **Amount:** ${result.get('amount', 0.0):.2f}\n"
            if 'reason' in result:
                report += f"- **Reason:** {result['reason']}\n"
            if 'invoice_id' in result:
                report += f"- **Invoice ID:** {result['invoice_id']}\n"
            if 'error' in result:
                report += f"- **Error:** {result['error']}\n"
            report += "\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Accounting Specialist Agent')
    parser.add_argument('--vault', default='./vault', help='Vault path')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--no-dry-run', action='store_false', dest='dry_run', help='Live mode')
    parser.add_argument('--file', type=str, help='Process specific file')
    parser.add_argument('--report', action='store_true', help='Generate report')

    args = parser.parse_args()

    agent = AccountingSpecialistAgent(vault_path=args.vault, dry_run=args.dry_run)

    if args.file:
        result = agent.process_invoice(Path(args.file))
        print(f"\nResult: {result}")
    else:
        results = agent.process_all_invoices()
        
        if args.report:
            report = agent.generate_report(results)
            print(report)
            
            report_file = Path(args.vault) / "Logs" / f"accounting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report_file.write_text(report)
            print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    main()
