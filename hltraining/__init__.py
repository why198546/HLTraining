"""Application factory for HLTraining.
Phased refactor: temporarily returns the existing Flask app from root `app.py`.
"""
from typing import Any

def create_app() -> Any:
    # Import the existing app instance to preserve current behavior
    from app import app as flask_app  # noqa: F401
    return flask_app
