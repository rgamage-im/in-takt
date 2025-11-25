#!/bin/bash
# Azure PostgreSQL Database Setup for In-Takt Portal
# This script helps create a new database in your Azure PostgreSQL server

set -e  # Exit on error

echo "============================================="
echo "Azure PostgreSQL Database Setup"
echo "============================================="
echo ""

# Azure PostgreSQL server details
SERVER_NAME="takt-land-search-postgres.postgres.database.azure.com"
DATABASE_NAME="intakt"
PORT="5432"

echo "Server: $SERVER_NAME"
echo "Database to create: $DATABASE_NAME"
echo ""

# Prompt for username
read -p "Enter your PostgreSQL username (e.g., rgamage or darwin-rg): " USERNAME

# Prompt for password (hidden input)
read -sp "Enter your PostgreSQL password: " PASSWORD
echo ""

# URL-encode the password for use in connection string
URL_ENCODED_PASSWORD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$PASSWORD', safe=''))")

# Note: Azure PostgreSQL Flexible Server uses just the username (not username@servername)
FULL_USERNAME="${USERNAME}"

echo ""
echo "Connecting to Azure PostgreSQL server..."
echo "Using username: $FULL_USERNAME"
echo ""

# Try to connect and create database
export PGPASSWORD="$PASSWORD"
export PGSSLMODE="require"

# First, list existing databases
echo "Listing existing databases..."
# Use PGPASSWORD env var to avoid special character issues in connection string
psql -h "$SERVER_NAME" -U "$FULL_USERNAME" -d postgres -p "$PORT" -c "\l" || {
    echo ""
    echo "Failed to connect. Common issues:"
    echo "1. Wrong password - verify in VS Code settings what password works"
    echo "2. Firewall: Add your current IP address in Azure Portal > PostgreSQL > Networking"
    echo "3. Username mismatch - check what username VS Code uses to connect"
    echo "4. Try running with the username format VS Code uses (check your VS Code connection settings)"
    exit 1
}

echo ""
echo "Creating database '$DATABASE_NAME' if it doesn't exist..."

# Create the database (ignore error if it already exists)
psql -h "$SERVER_NAME" -U "$FULL_USERNAME" -d postgres -p "$PORT" -c "CREATE DATABASE $DATABASE_NAME;" 2>/dev/null || {
    echo "Database may already exist, continuing..."
}

echo ""
echo "Verifying database exists..."
psql -h "$SERVER_NAME" -U "$FULL_USERNAME" -d postgres -p "$PORT" -c "\l" | grep "$DATABASE_NAME"

echo ""
echo "============================================="
echo "Database setup complete!"
echo "============================================="
echo ""
echo "Your DATABASE_URL for production (add to Azure App Service settings):"
echo ""
echo "DATABASE_URL=postgresql://${FULL_USERNAME}:${URL_ENCODED_PASSWORD}@${SERVER_NAME}:${PORT}/${DATABASE_NAME}?sslmode=require"
echo ""
echo "IMPORTANT: Do NOT add this to your local .env file!"
echo "Keep using SQLite locally. Only add DATABASE_URL to Azure App Service > Configuration > Application settings"
echo ""
echo "Next steps:"
echo "1. Update your .env file with the DATABASE_URL above"
echo "2. Run: python manage.py migrate"
echo "3. Run: python manage.py createsuperuser"
echo ""

# Clean up password from environment
unset PGPASSWORD
unset PGSSLMODE
