"""WSGI entrypoint for production servers (gunicorn/uwsgi).
Directly imports the Flask app from the root app.py module.
"""
import sys
import os

# Add the project root to sys.path (must be first to override package imports)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT in sys.modules:
    # Remove 'app' package from cache if it exists
    if 'app' in sys.modules:
        del sys.modules['app']

# Now import directly from app.py module
# We need to use importlib to bypass the app/ package
import importlib.util
app_spec = importlib.util.spec_from_file_location("app_module", os.path.join(PROJECT_ROOT, "app.py"))
app_module = importlib.util.module_from_spec(app_spec)
app_spec.loader.exec_module(app_module)

application = app_module.app

