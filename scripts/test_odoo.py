#!/usr/bin/env python3
"""
Odoo MCP Server Test Script

Tests all Odoo MCP server functions without requiring full orchestrator.
Run this after starting Odoo via Docker.

Usage:
    python scripts/test_odoo.py
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.odoo.server import (
    odoo_status,
    create_customer,
    list_customers,
    create_invoice,
    list_invoices,
    post_invoice,
    create_payment,
    list_payments,
    get_financial_summary,
    get_account_moves,
)


def test_odoo_connection():
    """Test basic Odoo connection"""
    print("\n" + "="*60)
    print("TEST 1: Odoo Connection")
    print("="*60)
    
    try:
        status = odoo_status()
        print(f"✅ Connection Status: {status.get('status', 'unknown')}")
        print(f"   URL: {status.get('url', 'N/A')}")
        print(f"   Database: {status.get('database', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("\nTroubleshooting:")
        print("1. Is Odoo running? Check: docker-compose ps")
        print("2. Is ODOO_URL correct? (should be http://localhost:8069)")
        print("3. Are credentials set in .env file?")
        return False


def test_create_customer():
    """Test customer creation"""
    print("\n" + "="*60)
    print("TEST 2: Create Customer")
    print("="*60)
    
    try:
        result = create_customer(
            name="Test Customer",
            email="test@example.com",
            phone="+1234567890",
            company_name="Test Company"
        )
        print(f"✅ Customer Created: {result.get('name', 'Unknown')}")
        print(f"   ID: {result.get('id', 'N/A')}")
        print(f"   Email: {result.get('email', 'N/A')}")
        return True, result.get('id')
    except Exception as e:
        print(f"❌ Customer Creation Failed: {e}")
        return False, None


def test_list_customers():
    """Test listing customers"""
    print("\n" + "="*60)
    print("TEST 3: List Customers")
    print("="*60)
    
    try:
        result = list_customers(limit=5)
        customers = result.get('customers', [])
        print(f"✅ Found {len(customers)} customers")
        for customer in customers[:3]:
            print(f"   - {customer.get('name', 'Unknown')} ({customer.get('email', 'No email')})")
        return True
    except Exception as e:
        print(f"❌ List Customers Failed: {e}")
        return False


def test_create_invoice():
    """Test invoice creation"""
    print("\n" + "="*60)
    print("TEST 4: Create Invoice")
    print("="*60)
    
    try:
        # First, get or create a customer
        customers_result = list_customers(limit=1)
        customers = customers_result.get('customers', [])
        
        if customers:
            customer = customers[0]
            customer_name = customer.get('name')
            customer_email = customer.get('email')
        else:
            # Create test customer
            create_customer(
                name="Invoice Test Customer",
                email="invoice-test@example.com"
            )
            customer_name = "Invoice Test Customer"
            customer_email = "invoice-test@example.com"
        
        # Create invoice
        invoice_lines = [
            {
                'name': 'Consulting Services - January 2026',
                'quantity': 10,
                'price_unit': 150.00,
            },
            {
                'name': 'Software License',
                'quantity': 1,
                'price_unit': 500.00,
            }
        ]
        
        result = create_invoice(
            partner_name=customer_name,
            partner_email=customer_email,
            invoice_lines=invoice_lines,
            payment_terms=30
        )
        
        print(f"✅ Invoice Created")
        print(f"   ID: {result.get('id', 'N/A')}")
        print(f"   Number: {result.get('number', 'N/A')}")
        print(f"   Total: ${result.get('amount_total', 0):.2f}")
        return True, result.get('id')
    except Exception as e:
        print(f"❌ Invoice Creation Failed: {e}")
        return False, None


def test_list_invoices():
    """Test listing invoices"""
    print("\n" + "="*60)
    print("TEST 5: List Invoices")
    print("="*60)
    
    try:
        result = list_invoices(limit=5)
        invoices = result.get('invoices', [])
        print(f"✅ Found {len(invoices)} invoices")
        for invoice in invoices[:3]:
            print(f"   - {invoice.get('number', 'Draft')} | ${invoice.get('amount_total', 0):.2f} | {invoice.get('state', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ List Invoices Failed: {e}")
        return False


def test_post_invoice(invoice_id):
    """Test posting/confirming an invoice"""
    print("\n" + "="*60)
    print("TEST 6: Post Invoice")
    print("="*60)
    
    if not invoice_id:
        print("⚠️  No invoice ID available, skipping test")
        return True
    
    try:
        result = post_invoice(invoice_id)
        print(f"✅ Invoice Posted")
        print(f"   ID: {invoice_id}")
        print(f"   Status: {result.get('status', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Post Invoice Failed: {e}")
        return False


def test_create_payment(invoice_id):
    """Test creating a payment"""
    print("\n" + "="*60)
    print("TEST 7: Create Payment")
    print("="*60)
    
    if not invoice_id:
        print("⚠️  No invoice ID available, skipping test")
        return True
    
    try:
        result = create_payment(
            invoice_id=invoice_id,
            amount=2000.00,
            payment_reference="Test Payment - January 2026"
        )
        print(f"✅ Payment Created")
        print(f"   Amount: ${result.get('amount', 0):.2f}")
        print(f"   Reference: {result.get('reference', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Payment Creation Failed: {e}")
        return False


def test_list_payments():
    """Test listing payments"""
    print("\n" + "="*60)
    print("TEST 8: List Payments")
    print("="*60)
    
    try:
        result = list_payments(limit=5)
        payments = result.get('payments', [])
        print(f"✅ Found {len(payments)} payments")
        for payment in payments[:3]:
            print(f"   - ${payment.get('amount', 0):.2f} | {payment.get('reference', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ List Payments Failed: {e}")
        return False


def test_financial_summary():
    """Test getting financial summary"""
    print("\n" + "="*60)
    print("TEST 9: Financial Summary")
    print("="*60)
    
    try:
        result = get_financial_summary(period_days=30)
        print(f"✅ Financial Summary Retrieved")
        print(f"   Revenue: ${result.get('revenue', 0):.2f}")
        print(f"   Expenses: ${result.get('expenses', 0):.2f}")
        print(f"   Profit: ${result.get('profit', 0):.2f}")
        print(f"   Invoices: {result.get('invoice_count', 0)}")
        print(f"   Payments: {result.get('payment_count', 0)}")
        return True
    except Exception as e:
        print(f"❌ Financial Summary Failed: {e}")
        return False


def test_account_moves():
    """Test getting account moves"""
    print("\n" + "="*60)
    print("TEST 10: Account Moves")
    print("="*60)
    
    try:
        result = get_account_moves(limit=5)
        moves = result.get('moves', [])
        print(f"✅ Found {len(moves)} account moves")
        for move in moves[:3]:
            print(f"   - {move.get('name', 'Unknown')} | {move.get('date', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Account Moves Failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ODOO MCP SERVER - COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Odoo URL: {os.getenv('ODOO_URL', 'http://localhost:8069')}")
    print(f"Database: {os.getenv('ODOO_DB', 'odoo')}")
    print(f"Dry Run: {os.getenv('DRY_RUN', 'true')}")
    
    results = {
        'passed': 0,
        'failed': 0,
        'skipped': 0
    }
    
    # Test 1: Connection
    if test_odoo_connection():
        results['passed'] += 1
    else:
        results['failed'] += 1
        print("\n❌ Connection failed. Skipping remaining tests.")
        print("\nPlease ensure:")
        print("1. Odoo is running: cd docker/odoo && docker-compose up -d")
        print("2. .env file has correct credentials")
        print("3. API key is generated in Odoo settings")
        return
    
    # Test 2: Create Customer
    success, customer_id = test_create_customer()
    if success:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 3: List Customers
    if test_list_customers():
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 4: Create Invoice
    success, invoice_id = test_create_invoice()
    if success:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 5: List Invoices
    if test_list_invoices():
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 6: Post Invoice
    if test_post_invoice(invoice_id):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 7: Create Payment
    if test_create_payment(invoice_id):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 8: List Payments
    if test_list_payments():
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 9: Financial Summary
    if test_financial_summary():
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 10: Account Moves
    if test_account_moves():
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"⚠️  Skipped: {results['skipped']}")
    print(f"📊 Total: {results['passed'] + results['failed'] + results['skipped']}")
    
    if results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED! Odoo MCP server is working correctly.")
        print("\nNext Steps:")
        print("1. Configure .env with DRY_RUN=false for real actions")
        print("2. Test via orchestrator: python orchestrator.py --vault ./vault")
        print("3. Create invoices via AI Employee workflow")
    else:
        print(f"\n⚠️  {results['failed']} test(s) failed. Please check errors above.")
    
    print("="*60)


if __name__ == "__main__":
    main()
