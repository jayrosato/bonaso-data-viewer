echo "Running Django collectstatic..."
python manage.py collectstatic --noinput
python manage.py migrate