#!/usr/bin/env bash
#
# MongoDB Docker Setup Script
#
# Goal: Automate the setup and deployment of a local MongoDB instance using Docker
#       for development and testing purposes.
#
# Features:
# - Installs Docker if not present
# - Pulls a MongoDB image
# - Creates a container with configured credentials
# - Binds to localhost only for security
#
# Usage:
#     bash start_mongo.sh
#
# Connection Details:
#     host=127.0.0.1 port=27017 user=mongoadmin password=secret authSource=admin
#

set -euo pipefail

echo "=== MongoDB Docker Setup ==="
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

echo "Step 4/6: Pulling MongoDB image..."
docker pull mongo:7
echo "  ✓ MongoDB image pulled"

echo "Step 5/6: Cleaning up old container (if exists)..."
if docker ps -a --format '{{.Names}}' | grep -Eq "^mongo-local\$"; then
  echo "  • Stopping and removing existing 'mongo-local' container..."
  docker rm -f mongo-local
  echo "  ✓ Old container removed"
else
  echo "  ✓ No existing container found"
fi

echo "Step 6/6: Creating new MongoDB container..."
docker run -d \
  --name mongo-local \
  -e MONGO_INITDB_ROOT_USERNAME=mongoadmin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  -p 127.0.0.1:27017:27017 \
  mongo:7

echo "  ✓ MongoDB container started"
echo ""
echo "Waiting for MongoDB to be ready..."
sleep 10

echo ""
echo "=== Setup Complete ==="
echo ""
echo "MongoDB is now running. Connect using:"
echo "  Host:     127.0.0.1"
echo "  Port:     27017"
echo "  User:     mongoadmin"
echo "  Password: secret"
echo "  Auth DB:  admin"
echo ""
echo "Connection string:"
echo "  mongodb://mongoadmin:secret@127.0.0.1:27017/?authSource=admin"
