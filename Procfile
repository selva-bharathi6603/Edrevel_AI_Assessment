web: gunicorn -b 0.0.0.0:8000 wsgi:app
work: ./manage.py rq worker
scheduler: ./manage.py rq scheduler
