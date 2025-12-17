#!/bin/bash

# NBA Analytics Engine - Setup Script
# ====================================

set -e # Exit on error

echo "🏀 NBA Analytics Engine - Setup"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
  echo "📝 Creating .env file from template..."
  cp .env.example .env

  echo "🔑 Generating Airflow Fernet key..."
  FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

  # Update .env with generated keys
  sed -i.bak "s|your_fernet_key_here|$FERNET_KEY|g" .env
  sed -i.bak "s|your_secret_key_here|$(openssl rand -hex 32)|g" .env

  rm .env.bak 2>/dev/null || true

  echo "✅ .env file created and configured"
else
  echo "ℹ️  .env file already exists, skipping..."
fi

echo ""
echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy (this may take 2-3 minutes)..."
sleep 30

echo ""
echo "🗄️  Initializing database..."
docker-compose exec -T postgres psql -U postgres -d nba_analytics -f /docker-entrypoint-initdb.d/setup_db.sql || echo "⚠️  Database already initialized"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Access your applications:"
echo "  - Airflow UI: http://localhost:8080 (admin/admin)"
echo "  - Streamlit Dashboard: http://localhost:8501"
echo "  - PostgreSQL: localhost:5432 (postgres/postgres)"
echo ""
echo "📚 Next steps:"
echo "  1. Visit http://localhost:8080 and login to Airflow"
echo "  2. Trigger the 'nba_daily_refresh' DAG to load sample data"
echo "  3. Visit http://localhost:8501 to see the dashboard"
echo ""
echo "🆘 Need help? Check QUICK_START.md"
