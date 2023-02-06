"""Using configuration for gunicorn"""
import os


LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logconfig = "logging.conf"

bind = "0.0.0.0:5000"
workers = 4
timeout = 1000
max_requests = 1000
max_requests_jitter = 42

# Make it False if used in production environment and not in development environment
reload = False
