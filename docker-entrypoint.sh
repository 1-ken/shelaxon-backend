#!/bin/bash

# Exit on error
set -e

echo "Waiting for MySQL to be ready..."
while ! nc -z db 3306; do
  sleep 0.5
done
echo "MySQL is ready!"

echo "Waiting for Redis to be ready..."
while ! nc -z redis 6379; do
  sleep 0.5
done
echo "Redis is ready!"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if it doesn't exist..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@retailconnect.com', 'admin123', business_name='Admin', phone_number='+254700000000', location='Nairobi', city='Nairobi')
    print('Superuser created!')
else:
    print('Superuser already exists!')
END

echo "Starting server..."
exec "$@"
