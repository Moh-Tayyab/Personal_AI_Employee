# Odoo Docker Setup Guide

This directory contains Docker Compose configuration for running Odoo Community Edition locally.

## Quick Start

### 1. Start Odoo

```bash
cd docker/odoo
docker-compose up -d
```

This will start:
- **PostgreSQL 15** on port 5432
- **Odoo 17.0 Community** on port 8069

### 2. Initial Setup

1. Open browser: http://localhost:8069
2. Create database:
   - Master password: `admin`
   - Database name: `odoo`
   - Email: your email
   - Password: choose a password
3. Select "Accounting" app during setup

### 3. Generate API Key

1. Login to Odoo as admin
2. Go to **Settings** → **Users**
3. Click on your user (admin)
4. Click **Actions** → **Change Password**
5. Generate an **API Key** (not just a password)
6. Copy the API key

### 4. Configure Environment Variables

Create or update `.env` file in project root:

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_API_KEY=your_api_key_here
```

### 5. Test Connection

```bash
# Test Odoo MCP server
python mcp/odoo/server.py

# Or use the test script
python scripts/test_odoo.py
```

## Common Commands

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f odoo
docker-compose logs -f db
```

### Stop Odoo
```bash
docker-compose down
```

### Reset Database
```bash
docker-compose down -v
docker-compose up -d
```

### Update Odoo Image
```bash
docker-compose pull
docker-compose up -d
```

## Troubleshooting

### Odoo Won't Start
```bash
# Check logs
docker-compose logs odoo

# Restart services
docker-compose restart
```

### Can't Connect to Odoo
```bash
# Verify it's running
curl http://localhost:8069

# Check port is not in use
lsof -i :8069
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps db

# Test connection
docker-compose exec db pg_isready -U odoo
```

## Odoo MCP Server Tools

Once connected, the MCP server provides these tools:

1. **odoo_status** - Check connection status
2. **create_customer** - Create new customer
3. **list_customers** - List all customers
4. **create_invoice** - Create invoice
5. **list_invoices** - List invoices
6. **post_invoice** - Confirm/post invoice
7. **create_payment** - Record payment
8. **list_payments** - List payments
9. **get_financial_summary** - Get financial reports
10. **get_account_moves** - Get journal entries

## Next Steps

After setup:
1. Configure your business chart of accounts
2. Add your products/services
3. Add your customers
4. Test invoice creation via MCP
5. Integration with AI Employee workflow
