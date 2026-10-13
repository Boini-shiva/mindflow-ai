import os
import sys
from pathlib import Path

# Add backend directory to sys.path so app package can be resolved
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Import the FastAPI application instance
from app.main import app

__all__ = ["app"]
