#!/bin/bash
set -euo pipefail

DEPLOY_DIR="/home/yutookiguchi/zeitan-dev-staging"
BRANCH="develop"

echo "=== Deploying STAGING (${BRANCH}) ==="

cd "$DEPLOY_DIR"

# Pull latest code
git fetch origin "$BRANCH"
git reset --hard "origin/${BRANCH}"

# Backend: install dependencies
venv/bin/pip install -q -r requirements.txt

# Stop staging services to free memory for build
sudo systemctl stop zeitan-staging-backend || true
sudo systemctl stop zeitan-staging-frontend || true

# Frontend: install dependencies + build
cd frontend
npm ci --prefer-offline
NODE_OPTIONS="--max_old_space_size=384" npm run build
cd ..

# Start services
sudo systemctl start zeitan-staging-backend
sudo systemctl start zeitan-staging-frontend

# Wait for backend to be ready
echo "Waiting for backend..."
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8004/health > /dev/null 2>&1; then
    echo "Backend is healthy"
    break
  fi
  if [ "$i" -eq 60 ]; then
    echo "ERROR: Backend failed to start"
    sudo journalctl -u zeitan-staging-backend --no-pager -n 20
    exit 1
  fi
  sleep 2
done

echo "=== Staging deploy complete ==="
