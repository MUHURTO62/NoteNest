#!/bin/bash
set -o errexit

echo "Running Django migrations..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
python backend/manage.py migrate --noinput

echo "Collecting static files..."
python backend/manage.py collectstatic --noinput

echo "Build complete!"
