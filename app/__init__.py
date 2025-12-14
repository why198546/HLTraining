"""App factory skeleton for phased refactor.
Currently returns the existing Flask app defined in root `app.py`.
This keeps runtime stable while we reorganize incrementally.
"""

from typing import Any

def create_app() -> Any:
    # Import the existing app instance to preserve behavior
    from app import app as flask_app  # type: ignore
    return flask_app
