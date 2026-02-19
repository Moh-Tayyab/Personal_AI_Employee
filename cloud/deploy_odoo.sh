#!/bin/bash
# Odoo Deployment Script - Deploy Odoo Community to cloud VM
# Usage: ./deploy_odoo.sh

set -e

echo "Deploying Odoo Community Edition..."

ODOO_VERSION="17.0"
INSTALL_PATH="/opt/odoo"
DB_USER="odoo"
DB_PASS="odoo"
DB_NAME="odoo"

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y postgresql postgresql-contrib wget git gcc python3-dev libxml2-dev libxslt1-dev libjpeg-dev libpng-dev libpq-dev

# Create Odoo user
useradd -m -U -r -s /bin/bash odoo
usermod -aG sudo odoo

# Install wkhtmltopdf (for PDF reports)
apt install -y wkhtmltopdf

# Install Python dependencies
apt install -y python3-pip python3-venv

# Clone Odoo
cd /opt
git clone --depth 1 --branch $ODOO_VERSION https://www.github.com/odoo/odoo odoo

# Create virtual environment
python3 -m venv $INSTALL_PATH/odoo-venv
source $INSTALL_PATH/odoo-venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r $INSTALL_PATH/odoo/requirements.txt

# Create log directory
mkdir -p /var/log/odoo
chown odoo:odoo /var/log/odoo

# Configure Odoo
cp $INSTALL_PATH/odoo/debian/odoo.conf /etc/odoo.conf

# Edit configuration
cat > /etc/odoo.conf << EOF
[options]
; This is the password that allows database operations:
admin_passwd = admin
db_host = False
db_port = False
db_user = $DB_USER
db_password = $DB_PASS
addons_path = $INSTALL_PATH/odoo/addons
logfile = /var/log/odoo/odoo.log
xmlrpc_port = 8069
; Enable HTTPS (configure nginx for this)
; proxy_mode = True
EOF

chown odoo:odoo /etc/odoo.conf
chmod 640 /etc/odoo.conf

# Setup PostgreSQL
su - postgres -c "psql -c \"CREATE USER $DB_USER WITH PASSWORD '$DB_PASS' CREATEDB;\""
su - postgres -c "psql -c \"ALTER USER $DB_USER WITH SUPERUSER;\""

# Create systemd service
cat > /etc/systemd/system/odoo.service << EOF
[Unit]
Description=Odoo
After=postgresql.service

[Service]
Type=simple
User=odoo
Group=odoo
ExecStart=$INSTALL_PATH/odoo-venv/bin/python $INSTALL_PATH/odoo/odoo-bin -c /etc/odoo.conf
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start Odoo
systemctl daemon-reload
systemctl enable odoo
systemctl start odoo

echo "Odoo deployed successfully!"
echo "Access at: http://YOUR_VM_IP:8069"
echo "Master password: admin"
