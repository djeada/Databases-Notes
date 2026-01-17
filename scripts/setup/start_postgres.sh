#!/usr/bin/env bash
#
# PostgreSQL Docker Setup Script
#
# Goal: Automate the setup and deployment of a local PostgreSQL instance using Docker
#       for development and testing purposes.
#
# Features:
# - Installs Docker if not present
# - Pulls the latest PostgreSQL image
# - Creates a container with configured database credentials
# - Binds to localhost only for security
#
# Usage:
#     bash start_postgres.sh
#
# Connection Details:
#     host=127.0.0.1 port=5432 dbname=test user=demo password=secret
#

set -euo pipefail

echo "=== PostgreSQL Docker Setup ==="
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

echo "Step 4/6: Pulling PostgreSQL image..."
docker pull postgres:latest
echo "  ✓ PostgreSQL image pulled"

echo "Step 5/6: Cleaning up old container (if exists)..."
if docker ps -a --format '{{.Names}}' | grep -Eq "^postgres-local\$"; then
  echo "  • Stopping and removing existing 'postgres-local' container..."
  docker rm -f postgres-local
  echo "  ✓ Old container removed"
else
  echo "  ✓ No existing container found"
fi

echo "Step 6/6: Creating new PostgreSQL container..."
docker run -d \
  --name postgres-local \
  -e POSTGRES_DB=test \
  -e POSTGRES_USER=demo \
  -e POSTGRES_PASSWORD=secret \
  -p 127.0.0.1:5432:5432 \
  postgres:latest

echo "  ✓ PostgreSQL container started"
echo ""
echo "=== Setup Complete ==="
echo ""
echo "PostgreSQL is now running. Connect using:"
echo "  Host:     127.0.0.1"
echo "  Port:     5432"
echo "  Database: test"
echo "  User:     demo"
echo "  Password: secret"
echo ""
echo "Connection string:"
echo "  postgresql://demo:secret@127.0.0.1:5432/test"
