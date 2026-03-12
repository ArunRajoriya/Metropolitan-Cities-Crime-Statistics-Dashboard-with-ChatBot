#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""
import os
from app import app

if __name__ == "__main__":
    # For development
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    # For production (Gunicorn, uWSGI, etc.)
    application = app