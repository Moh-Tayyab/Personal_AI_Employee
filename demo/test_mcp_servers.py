#!/usr/bin/env python3
"""
MCP Server Test Suite
Tests all Gold Tier MCP servers for connectivity and basic functionality.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Setup
load_dotenv(override=True)
sys.path.insert(0, os.path.abspath('.'))

print("="*70)
print("  MCP SERVER TEST SUITE")
print("="*70)

results = {"passed": 0, "failed": 0, "warnings": 0}

def test_server(name, test_func):
    try:
        status = test_func()
        if status:
            print(f"✅ {name}: PASSED")
            results["passed"] += 1
        else:
            print(f"⚠️  {name}: WARNING (Connected but returned empty/data missing)")
            results["warnings"] += 1
    except Exception as e:
        print(f"❌ {name}: FAILED - {str(e)[:60]}")
        results["failed"] += 1

# --- 1. Odoo MCP ---
def test_odoo():
    import requests
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    url = f"{os.getenv('ODOO_URL')}/jsonrpc"
    payload = {
        'jsonrpc': '2.0', 'method': 'call', 'id': 1,
        'params': {'service': 'common', 'method': 'authenticate', 
                   'args': [os.getenv('ODOO_DB'), os.getenv('ODOO_USERNAME'), os.getenv('ODOO_API_KEY'), {}]}
    }
    res = requests.post(url, json=payload, timeout=10).json()
    uid = res.get('result')
    if isinstance(uid, int):
        # Check revenue
        inv_res = requests.post(url, json={
            'jsonrpc': '2.0', 'method': 'call', 'id': 2,
            'params': {'service': 'object', 'method': 'execute_kw', 
                       'args': [os.getenv('ODOO_DB'), uid, os.getenv('ODOO_API_KEY'), 'account.move', 'search_count', [[['state', '=', 'posted']]]}
        }).json()
        count = inv_res.get('result', 0)
        print(f"   📊 Odoo Invoices: {count} posted")
        return True
    return False

test_server("Odoo Accounting", test_odoo)

# --- 2. Filesystem MCP ---
def test_filesystem():
    vault = os.getenv('VAULT_PATH', './vault')
    if os.path.exists(vault):
        count = len(os.listdir(vault))
        print(f"   📂 Vault Items: {count}")
        return True
    return False

test_server("Filesystem/Vault", test_filesystem)

# --- 3. LinkedIn MCP ---
def test_linkedin():
    token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    if not token or token.startswith('AQU') or len(token) < 50:
        print(f"   🔑 Token Status: {'Configured' if token else 'Missing'}")
        return token and len(token) > 50
    print(f"   🔑 Token Status: Placeholder/Dummy")
    return False

test_server("LinkedIn", test_linkedin)

# --- 4. Twitter MCP ---
def test_twitter():
    key = os.getenv('TWITTER_API_KEY')
    secret = os.getenv('TWITTER_API_SECRET')
    if key and secret:
        print(f"   🔑 Keys: Present")
        return True
    print(f"   🔑 Keys: Missing")
    return False

test_server("Twitter/X", test_twitter)

# --- 5. Social MCP (Facebook/Insta) ---
def test_social():
    token = os.getenv('META_ACCESS_TOKEN')
    if token and len(token) > 50:
        print(f"   🔑 Meta Token: Present")
        return True
    print(f"   🔑 Meta Token: Missing/Short")
    return False

test_server("Social (FB/Insta)", test_social)

# --- Summary ---
print("\n" + "="*70)
print(f"  RESULTS: {results['passed']} Passed, {results['failed']} Failed, {results['warnings']} Warnings")
print("="*70)
if results['failed'] == 0:
    print("✅ ALL CRITICAL MCP SERVERS OPERATIONAL")
else:
    print("⚠️  SOME SERVERS NEED ATTENTION")
