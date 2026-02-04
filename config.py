import os

inventree_url = os.getenv("INVENTREE_SERVER", "http://inventree-server:8000")
inv_user = os.getenv("INVENTREE_ADMIN_USER")
inv_pass = os.getenv("INVENTREE_ADMIN_PASSWORD")
