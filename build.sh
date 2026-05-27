#!/bin/bash
set -o errexit

echo "Running Django migrations..."
python backend/manage.py migrate --noinput

echo "Collecting static files..."
python backend/manage.py collectstatic --noinput

echo "Build complete!"
