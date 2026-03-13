#!/bin/bash
set -euo pipefail

DEPLOY_DIR="/home/yutookiguchi/zeitan-dev"
BRANCH="main"

echo "=== Deploying PRODUCTION (${BRANCH}) ==="

cd "$DEPLOY_DIR"

# Pull latest code
git fetch origin "$BRANCH"
git reset --hard "origin/${BRANCH}"

# Backend: install dependencies
venv/bin/pip install -q -r requirements.txt

# Stop services to free memory for build
sudo systemctl stop zeitan-backend
sudo systemctl stop zeitan-frontend

# Frontend: install dependencies + build
cd frontend
npm ci --prefer-offline
NODE_OPTIONS="--max_old_space_size=384" npm run build
cd ..

# Start services
sudo systemctl start zeitan-backend
sudo systemctl start zeitan-frontend

# Wait for backend to be ready
echo "Waiting for backend..."
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8003/health > /dev/null 2>&1; then
    echo "Backend is healthy"
    break
  fi
  if [ "$i" -eq 60 ]; then
    echo "ERROR: Backend failed to start"
    sudo journalctl -u zeitan-backend --no-pager -n 20
    exit 1
  fi
  sleep 2
done

echo "=== Production deploy complete ==="
