import os

# InvenTree API
BASE_URL = os.getenv("INVENTREE_SERVER", "http://inventree-server:8000")
INV_USER = os.getenv("INVENTREE_ADMIN_USER")
INV_PASS = os.getenv("INVENTREE_ADMIN_PASSWORD")

# Okta (user sync)
OKTA_URL = os.getenv("OKTA_URL")
OKTA_API_KEY = os.getenv("OKTA_API_KEY")

# App
DEBUG = os.getenv("INVENTREE_DEBUG", "True").lower() in ("true", "1", "yes")
CONSOLE_SECRET_KEY = os.getenv("CONSOLE_SECRET_KEY", "change-me-in-production")
