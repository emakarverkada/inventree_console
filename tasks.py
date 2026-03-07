import logging
import re
import time

import requests

from config import OKTA_URL, OKTA_API_KEY
from inventree_calls import get_customers, add_customer, parse_json

logger = logging.getLogger(__name__)


class SSWS_Auth(requests.auth.AuthBase):
    """Attaches Okta SSWS API token to the request Authorization header."""

    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        return isinstance(other, SSWS_Auth) and self.token == other.token

    def __ne__(self, other):
        return not (self == other)

    def __call__(self, r):
        r.headers["Authorization"] = f"SSWS {self.token}"
        return r


class okta_auth:
    auth = None

    @classmethod
    def set_auth(cls, token):
        cls.auth = SSWS_Auth(token)

    def __init__(self, func=None):
        if func is not None:
            self.func = func
        else:
            print("no function")

    def __call__(self, *arg, **kwarg):
        """
        sets authentication to decorated function
        """
        ret = self.func(*arg, **kwarg, auth=self.auth)
        return ret


@okta_auth
def make_okta_request(method: str, path: str, **kwargs) -> requests.Response:
    """
    Helper function for calling Okta API.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: API path (e.g. /v1/users).

    Returns:
        requests.Response
    """
    url = OKTA_URL + "/api" + path
    logger.info("Okta API request: %s %s", method, path)
    start = time.perf_counter()
    try:
        response = requests.request(method=method, url=url, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("Okta API response: %s %s -> %d (%.0f ms)", method, path, response.status_code, elapsed_ms)
        return response
    except requests.RequestException as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.exception("Okta API error: %s %s failed after %.0f ms: %s", method, path, elapsed_ms, e)
        raise


VERKADA_EMAIL_PATTERN = re.compile(r"\w+\.\w+@verkada.com")


def get_okta_users():
    """
    Fetch users from Okta and return those with @verkada.com emails.

    Returns:
        List of dicts with "name" (first + last) and "email".
    """
    response = make_okta_request(method="GET", path="/v1/users")
    response.raise_for_status()
    okta_data = response.json()
    users = []

    for user in okta_data:
        profile = user["profile"]
        email = profile["email"]
        if VERKADA_EMAIL_PATTERN.match(email):
            full_name = f"{profile['firstName']} {profile['lastName']}"
            users.append({"name": full_name, "email": email})

    return users


def _dict_list_to_set(dict_list):
    """Convert a list of dicts to a set of frozensets for comparison."""
    return set(frozenset(d.items()) for d in dict_list)


def sync_okta_users():
    """Sync Okta users into InvenTree: add any Okta users not yet in customers."""
    current_customers = parse_json(get_customers(), ["name", "email"])
    okta_users = get_okta_users()

    current_set = _dict_list_to_set(current_customers)
    okta_set = _dict_list_to_set(okta_users)
    new_users = okta_set - current_set

    for user_frozen in new_users:
        user = dict(user_frozen)
        add_customer(user["name"], user["email"])
        logger.info("Sync added user: %s", user)
