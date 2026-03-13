#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/yutookiguchi/zeitan-dev"
STAGING_DIR="/home/yutookiguchi/zeitan-dev-staging"
PROD_DOMAIN="zeitan.soushu.biz"
STAGING_DOMAIN="dev.zeitan.soushu.biz"
GCP_PROJECT_ID="bitpoint-bot"

echo "=== Zeitan Deploy Setup ==="

# ---- 0. Prerequisites check ----
echo ">>> Checking prerequisites..."
for cmd in python3 node npm nginx certbot git curl; do
  command -v "$cmd" &> /dev/null || { echo "ERROR: $cmd not found"; exit 1; }
done
echo "All prerequisites found."

# ---- 1. Clone repositories ----
echo ">>> Setting up repositories..."
if [ ! -d "$APP_DIR" ]; then
  cd /home/yutookiguchi
  git clone https://github.com/soushu/zeitan-dev.git zeitan-dev
else
  echo "Production repo already exists, skipping clone."
fi

if [ ! -d "$STAGING_DIR" ]; then
  cd /home/yutookiguchi
  git clone https://github.com/soushu/zeitan-dev.git zeitan-dev-staging
  cd "$STAGING_DIR" && git checkout develop
else
  echo "Staging repo already exists, skipping clone."
fi

# ---- 2. Python venv + dependencies ----
echo ">>> Setting up Python venv (production)..."
cd "$APP_DIR"
if [ ! -d venv ]; then
  python3 -m venv venv
fi
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q

echo ">>> Setting up Python venv (staging)..."
cd "$STAGING_DIR"
if [ ! -d venv ]; then
  python3 -m venv venv
fi
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q

# ---- 3. PostgreSQL databases ----
echo ">>> Setting up PostgreSQL databases..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='zeitan'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE DATABASE zeitan OWNER claudia;"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='zeitan_staging'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE DATABASE zeitan_staging OWNER claudia;"
echo "Databases ready."

# ---- 4. Environment files ----
echo ">>> Checking environment files..."
for envfile in "$APP_DIR/.env" "$APP_DIR/frontend/.env.local" "$STAGING_DIR/.env" "$STAGING_DIR/frontend/.env.local"; do
  if [ ! -f "$envfile" ]; then
    echo "WARNING: $envfile does not exist. Create it manually."
  fi
done

# ---- 5. Frontend build ----
echo ">>> Building frontend (production)..."
cd "$APP_DIR/frontend"
npm ci --prefer-offline
NODE_OPTIONS="--max_old_space_size=384" npm run build

echo ">>> Building frontend (staging)..."
cd "$STAGING_DIR/frontend"
npm ci --prefer-offline
NODE_OPTIONS="--max_old_space_size=384" npm run build

# ---- 6. systemd services ----
echo ">>> Installing systemd services..."
sudo cp "$APP_DIR/deploy/zeitan-backend.service" /etc/systemd/system/
sudo cp "$APP_DIR/deploy/zeitan-frontend.service" /etc/systemd/system/
sudo cp "$APP_DIR/deploy/zeitan-staging-backend.service" /etc/systemd/system/
sudo cp "$APP_DIR/deploy/zeitan-staging-frontend.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable zeitan-backend zeitan-frontend
sudo systemctl enable zeitan-staging-backend zeitan-staging-frontend
sudo systemctl start zeitan-backend zeitan-frontend
sudo systemctl start zeitan-staging-backend zeitan-staging-frontend

# Wait for backends to start
echo ">>> Waiting for backends..."
sleep 5
curl -sf http://127.0.0.1:8003/health && echo " Production backend OK" || echo " WARNING: production backend health check failed"
curl -sf http://127.0.0.1:8004/health && echo " Staging backend OK" || echo " WARNING: staging backend health check failed"

# ---- 7. Nginx ----
echo ">>> Configuring Nginx..."
sudo cp "$APP_DIR/deploy/nginx/zeitan.conf" /etc/nginx/sites-available/zeitan
sudo cp "$APP_DIR/deploy/nginx/zeitan-staging.conf" /etc/nginx/sites-available/zeitan-staging
sudo ln -sf /etc/nginx/sites-available/zeitan /etc/nginx/sites-enabled/zeitan
sudo ln -sf /etc/nginx/sites-available/zeitan-staging /etc/nginx/sites-enabled/zeitan-staging
sudo nginx -t
sudo systemctl reload nginx

# ---- 8. SSL (certbot) ----
echo ">>> Setting up SSL..."
echo "Make sure DNS for ${PROD_DOMAIN} and ${STAGING_DOMAIN} points to this server's IP."
echo "Verify with: dig ${PROD_DOMAIN} +short"
read -rp "Run certbot now? [y/N] " yn
if [[ "$yn" =~ ^[Yy]$ ]]; then
  sudo certbot --nginx -d "$PROD_DOMAIN" --non-interactive --agree-tos -m admin@soushu.biz
  sudo certbot --nginx -d "$STAGING_DOMAIN" --non-interactive --agree-tos -m admin@soushu.biz
fi

# ---- 9. WIF (Workload Identity Federation) ----
echo ""
echo ">>> WIF setup required. Run the following command:"
echo ""
echo "gcloud iam service-accounts add-iam-policy-binding \\"
echo "  claudia-deploy@${GCP_PROJECT_ID}.iam.gserviceaccount.com \\"
echo "  --role=roles/iam.workloadIdentityUser \\"
echo "  --member=\"principalSet://iam.googleapis.com/projects/\$(gcloud projects describe ${GCP_PROJECT_ID} --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-actions/attribute.repository/soushu/zeitan-dev\""
echo ""

echo ""
echo "=== Setup complete ==="
echo "  Production backend:  systemctl status zeitan-backend"
echo "  Production frontend: systemctl status zeitan-frontend"
echo "  Staging backend:     systemctl status zeitan-staging-backend"
echo "  Staging frontend:    systemctl status zeitan-staging-frontend"
echo "  Nginx:               systemctl status nginx"
echo "  Production URL:      https://${PROD_DOMAIN}"
echo "  Staging URL:         https://${STAGING_DOMAIN}"
