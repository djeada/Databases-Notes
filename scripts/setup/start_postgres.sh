#!/usr/bin/env bash
set -euo pipefail

echo "=== 1. Updating package index ==="
sudo apt-get update -y

echo "=== 2. Installing Docker (if not already installed) ==="
if ! command -v docker &> /dev/null; then
  sudo apt-get install -y docker.io
else
  echo "Docker is already installed, skipping."
fi

echo "=== 3. Starting and enabling Docker service ==="
sudo systemctl start docker
sudo systemctl enable docker

echo "=== 4. Pulling latest Postgres image ==="
docker pull postgres:latest

echo "=== 5. Removing any old 'postgres-local' container ==="
if docker ps -a --format '{{.Names}}' | grep -Eq "^postgres-local\$"; then
  echo "Stopping and removing existing 'postgres-local' container..."
  docker rm -f postgres-local
fi

echo "=== 6. Running new Postgres container ==="
docker run -d \
  --name postgres-local \
  -e POSTGRES_DB=test \
  -e POSTGRES_USER=demo \
  -e POSTGRES_PASSWORD=secret \
  -p 127.0.0.1:5432:5432 \
  postgres:latest

echo "=== Done! ==="
echo "You can now connect with:"
echo "  host=127.0.0.1 port=5432 dbname=test user=demo password=secret"
