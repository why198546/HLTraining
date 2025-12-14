"""WSGI entrypoint for production servers (gunicorn/uwsgi).
Uses the temporary factory that returns the existing Flask app.
"""
from hltraining import create_app

application = create_app()
