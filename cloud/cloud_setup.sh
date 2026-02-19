#!/bin/bash
# Cloud Setup Script - Deploy Personal AI Employee to cloud VM
# Usage: ./cloud_setup.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Personal AI Employee - Cloud Deployment${NC}"

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."

    if ! command -v ssh &> /dev/null; then
        echo -e "${RED}Error: ssh not found${NC}"
        exit 1
    fi

    if ! command -v git &> /dev/null; then
        echo -e "${RED}Error: git not found${NC}"
        exit 1
    fi

    echo -e "${GREEN}Prerequisites OK${NC}"
}

# Setup cloud VM
setup_vm() {
    echo "Setting up cloud VM..."

    # Update system
    ssh $CLOUD_USER@$CLOUD_HOST "sudo apt update && sudo apt upgrade -y"

    # Install Python
    ssh $CLOUD_USER@$CLOUD_HOST "sudo apt install -y python3 python3-pip python3-venv"

    # Install Node.js
    ssh $CLOUD_USER@$CLOUD_HOST "curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -"
    ssh $CLOUD_USER@$CLOUD_HOST "sudo apt install -y nodejs"

    # Install PM2
    ssh $CLOUD_USER@$CLOUD_HOST "sudo npm install -g pm2"

    # Create project directory
    ssh $CLOUD_USER@$CLOUD_HOST "mkdir -p ~/personal-ai-employee"

    echo -e "${GREEN}VM setup complete${NC}"
}

# Deploy application
deploy() {
    echo "Deploying application..."

    # Copy files (exclude vault, secrets)
    rsync -av --exclude='.git' --exclude='vault' --exclude='.env' \
        --exclude='secrets' --exclude='*.session' \
        ./ $CLOUD_USER@$CLOUD_HOST:~/personal-ai-employee/

    # Install dependencies
    ssh $CLOUD_USER@$CLOUD_HOST "cd ~/personal-ai-employee && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"

    echo -e "${GREEN}Deployment complete${NC}"
}

# Start services
start_services() {
    echo "Starting services..."

    # Start orchestrator
    ssh $CLOUD_USER@$CLOUD_HOST "cd ~/personal-ai-employee && source .venv/bin/activate && pm2 start orchestrator.py --name orchestrator -- --vault ./vault"

    # Start watchers
    ssh $CLOUD_USER@$CLOUD_HOST "cd ~/personal-ai-employee && source .venv/bin/activate && pm2 start watchers/gmail_watcher.py --name gmail-watcher -- --vault ./vault"

    # Save PM2 config
    ssh $CLOUD_USER@$CLOUD_HOST "pm2 save"

    # Setup startup
    ssh $CLOUD_USER@$CLOUD_HOST "pm2 startup"

    echo -e "${GREEN}Services started${NC}"
}

# Main
main() {
    check_prerequisites
    setup_vm
    deploy
    start_services

    echo -e "${GREEN}Cloud deployment complete!${NC}"
    echo "Access your VM at: $CLOUD_USER@$CLOUD_HOST"
}

# Run
if [ "$1" = "quick" ]; then
    deploy
    start_services
else
    main
fi
