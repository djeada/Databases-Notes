#!/usr/bin/env bash
#
# MySQL Docker Setup Script
#
# Goal: Automate the setup and deployment of a local MySQL instance using Docker
#       for development and testing purposes.
#
# Features:
# - Installs Docker if not present
# - Pulls the latest MySQL image
# - Creates a container with configured database credentials
# - Binds to localhost only for security
#
# Usage:
#     bash start_mysql.sh
#
# Connection Details:
#     host=127.0.0.1 port=3306 dbname=testdb user=testuser password=testpass
#

set -euo pipefail

echo "=== MySQL Docker Setup ==="
echo ""

echo "Step 1/6: Updating package index..."
sudo apt-get update -y

echo "Step 2/6: Installing Docker (if needed)..."
if ! command -v docker &> /dev/null; then
  sudo apt-get install -y docker.io
  echo "  ✓ Docker installed"
else
  echo "  ✓ Docker already installed, skipping"
fi

echo "Step 3/6: Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker
echo "  ✓ Docker service started and enabled"

echo "Step 4/6: Pulling MySQL image..."
docker pull mysql:latest
echo "  ✓ MySQL image pulled"

echo "Step 5/6: Cleaning up old container (if exists)..."
if docker ps -a --format '{{.Names}}' | grep -Eq "^mysql-local\$"; then
  echo "  • Stopping and removing existing 'mysql-local' container..."
  docker rm -f mysql-local
  echo "  ✓ Old container removed"
else
  echo "  ✓ No existing container found"
fi

echo "Step 6/6: Creating new MySQL container..."
docker run -d \
  --name mysql-local \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=testdb \
  -e MYSQL_USER=testuser \
  -e MYSQL_PASSWORD=testpass \
  -p 127.0.0.1:3306:3306 \
  mysql:latest

echo "  ✓ MySQL container started"
echo ""
echo "Waiting for MySQL to be ready (this may take 10-20 seconds)..."
sleep 15

echo ""
echo "=== Setup Complete ==="
echo ""
echo "MySQL is now running. Connect using:"
echo "  Host:     127.0.0.1"
echo "  Port:     3306"
echo "  Database: testdb"
echo "  User:     testuser"
echo "  Password: testpass"
echo "  Root Password: rootpass"
echo ""
echo "Connection string:"
echo "  mysql://testuser:testpass@127.0.0.1:3306/testdb"
echo ""
echo "To connect via CLI:"
echo "  docker exec -it mysql-local mysql -u testuser -ptestpass testdb"
