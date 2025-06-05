echo "Running Django collectstatic..."
pip install -r requirements.txt
python manage.py collectstatic --noinput