#!/usr/bin/env bash
#
# Neo4j Docker Setup Script
#
# Goal: Automate the setup and deployment of a local Neo4j instance using Docker
#       for development and testing purposes.
#
# Features:
# - Installs Docker if not present
# - Pulls a Neo4j image
# - Creates a container with configured credentials
# - Binds to localhost only for security
#
# Usage:
#     bash start_neo4j.sh
#
# Connection Details:
#     host=127.0.0.1 bolt_port=7687 http_port=7474 user=neo4j password=testpass
#

set -euo pipefail

echo "=== Neo4j Docker Setup ==="
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

echo "Step 4/6: Pulling Neo4j image..."
docker pull neo4j:5
echo "  ✓ Neo4j image pulled"

echo "Step 5/6: Cleaning up old container (if exists)..."
if docker ps -a --format '{{.Names}}' | grep -Eq "^neo4j-local\$"; then
  echo "  • Stopping and removing existing 'neo4j-local' container..."
  docker rm -f neo4j-local
  echo "  ✓ Old container removed"
else
  echo "  ✓ No existing container found"
fi

echo "Step 6/6: Creating new Neo4j container..."
docker run -d \
  --name neo4j-local \
  -e NEO4J_AUTH=neo4j/testpass \
  -p 127.0.0.1:7474:7474 \
  -p 127.0.0.1:7687:7687 \
  neo4j:5

echo "  ✓ Neo4j container started"
echo ""
echo "Waiting for Neo4j to be ready..."
sleep 20

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Neo4j is now running. Connect using:"
echo "  Bolt URI:  bolt://127.0.0.1:7687"
echo "  HTTP URI:  http://127.0.0.1:7474"
echo "  User:      neo4j"
echo "  Password:  testpass"
