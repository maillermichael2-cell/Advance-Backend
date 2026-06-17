#!/bin/bash
set -e

echo "Waiting for database to be ready..."
while ! pg_isready -h db -U realty_user -d realty_db 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "Database is ready!"

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser if it doesn't exist..."
python manage.py shell << END
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@realty.com', 'admin123')
    print("Superuser 'admin' created successfully")
else:
    print("Superuser 'admin' already exists")
END

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django server..."
exec "$@"
