#!/usr/bin/env bash
set -euo pipefail

# Usage: sudo ./install_system_service.sh /path/to/project
# Example: sudo ./install_system_service.sh /home/ubuntu/pico-a1111-proxy

PROJECT_SRC_DIR="${1:-$(pwd)}"
INSTALL_DIR="/opt/pico-a1111-proxy"
SERVICE_FILE="/etc/systemd/system/pico-a1111-proxy.service"
NGINX_SITE="/etc/nginx/sites-available/pico-a1111-proxy"

if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root (sudo)" >&2
  exit 1
fi

echo "Installing Pico A1111 Proxy from $PROJECT_SRC_DIR -> $INSTALL_DIR"

rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp -r "$PROJECT_SRC_DIR"/* "$INSTALL_DIR/"

python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip setuptools wheel
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

cp "$INSTALL_DIR/deploy/pico-a1111-proxy.service" "$SERVICE_FILE"
systemctl daemon-reload
systemctl enable pico-a1111-proxy.service
systemctl restart pico-a1111-proxy.service

# Nginx site
cp "$INSTALL_DIR/deploy/nginx-pico-a1111-proxy.conf" "$NGINX_SITE"
ln -sf "$NGINX_SITE" /etc/nginx/sites-enabled/pico-a1111-proxy
systemctl reload nginx || true

echo "Deployment complete. Service status:"
systemctl status pico-a1111-proxy.service --no-pager
