import requests
import re

from config import OKTA_URL, OKTA_API_KEY
from inventree_calls import get_customers, add_customer, parse_json


class SSWS_Auth(requests.auth.AuthBase):
    """Attaches HTTP Basic Authentication to the given Request object."""

    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        return all(
            [
                self.token == getattr(other, "token", None),
            ]
        )

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers["Authorization"] = "SSWS {self.token}"
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
    Helper function for calling APIs

    Args:
        method: method used for calling the API
        path: API path on top of base URL

    Returns:
        Requests Response
    """
    url = OKTA_URL + "/api" + path
    response = requests.request(method=method, url=url, **kwargs)
    return response


def get_okta_users():
    """
    Returns list of dicts with displayname and email
    """
    path = "/v1/users"
    url = OKTA_URL + "/api" + path
    users = []
    headers = {"Authorization": "SSWS " + OKTA_API_KEY}
    response = requests.get(url=url, headers=headers)
    # response = make_okta_request(method="GET", path=path)
    response.raise_for_status()
    data = response.json()
    p = re.compile(r"\w+\.\w+@verkada.com")
    for i in data:
        if p.match(i["profile"]["email"]):
            users.append({"name": f"{i["profile"]["firstName"]} {i["profile"]["lastName"]}", "email": i["profile"]["email"]})

    return users


convert_to_set = lambda l: set(frozenset(d.items()) for d in l)


def sync_okta_users():
    current_users = parse_json(get_customers(), ["name", "email"])
    okta_users = get_okta_users()

    user_diff = convert_to_set(okta_users).difference(convert_to_set(current_users))
    for user in user_diff:
        user = dict(user)
        add_customer(user["name"], user["email"])
        print("Added user", user)
