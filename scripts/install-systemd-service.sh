#!/bin/bash
# =============================================================================
# uSipipo Backend - Systemd Service Installation Script
# =============================================================================
# This script installs and configures the systemd service for uSipipo backend
# Run with sudo: sudo bash scripts/install-systemd-service.sh
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="usipipo-backend"
SERVICE_FILE="deploy/usipipo-backend.service"
ENV_TEMPLATE="deploy/.env.template"
BACKEND_USER="usipipo"
BACKEND_GROUP="usipipo"
BACKEND_DIR="/home/usipipo/usipipo-backend"

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}uSipipo Backend - Systemd Setup${NC}"
echo -e "${GREEN}==================================${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Please run with sudo${NC}"
    exit 1
fi

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}Error: Service file not found: $SERVICE_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Creating user/group if not exists...${NC}"
if ! id -u $BACKEND_USER >/dev/null 2>&1; then
    useradd -r -m -s /bin/bash $BACKEND_USER
    echo -e "${GREEN}✓ Created user: $BACKEND_USER${NC}"
else
    echo -e "${GREEN}✓ User already exists: $BACKEND_USER${NC}"
fi

if ! getent group $BACKEND_GROUP >/dev/null 2>&1; then
    groupadd $BACKEND_GROUP
    echo -e "${GREEN}✓ Created group: $BACKEND_GROUP${NC}"
else
    echo -e "${GREEN}✓ Group already exists: $BACKEND_GROUP${NC}"
fi

echo -e "${YELLOW}Step 2: Setting directory permissions...${NC}"
mkdir -p $BACKEND_DIR/logs
chown -R $BACKEND_USER:$BACKEND_GROUP $BACKEND_DIR
chmod 755 $BACKEND_DIR
chmod 755 $BACKEND_DIR/logs
echo -e "${GREEN}✓ Directory permissions set${NC}"

echo -e "${YELLOW}Step 3: Installing systemd service...${NC}"
cp $SERVICE_FILE /etc/systemd/system/$SERVICE_NAME.service
chmod 644 /etc/systemd/system/$SERVICE_NAME.service
echo -e "${GREEN}✓ Service file installed${NC}"

echo -e "${YELLOW}Step 4: Reloading systemd daemon...${NC}"
systemctl daemon-reload
echo -e "${GREEN}✓ Systemd daemon reloaded${NC}"

echo -e "${YELLOW}Step 5: Enabling service...${NC}"
systemctl enable $SERVICE_NAME
echo -e "${GREEN}✓ Service enabled (will start on boot)${NC}"

echo -e "${YELLOW}Step 6: Checking environment file...${NC}"
if [ -f "$BACKEND_DIR/.env" ]; then
    echo -e "${GREEN}✓ Environment file exists: $BACKEND_DIR/.env${NC}"
else
    echo -e "${YELLOW}⚠ Environment file not found!${NC}"
    echo -e "${YELLOW}  Please copy $ENV_TEMPLATE to $BACKEND_DIR/.env${NC}"
    echo -e "${YELLOW}  and configure your environment variables.${NC}"
fi

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure environment: sudo nano $BACKEND_DIR/.env"
echo "2. Start service: sudo systemctl start $SERVICE_NAME"
echo "3. Check status: sudo systemctl status $SERVICE_NAME"
echo "4. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  sudo systemctl start $SERVICE_NAME    # Start service"
echo "  sudo systemctl stop $SERVICE_NAME     # Stop service"
echo "  sudo systemctl restart $SERVICE_NAME  # Restart service"
echo "  sudo systemctl reload $SERVICE_NAME   # Reload configuration"
echo "  sudo systemctl disable $SERVICE_NAME  # Disable on boot"
echo ""
