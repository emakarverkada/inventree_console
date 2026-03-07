import requests
from requests.auth import HTTPBasicAuth

from config import BASE_URL, DEBUG
import logging

logging.basicConfig(level=logging.DEBUG)


class basic_auth:
    auth = None

    @classmethod
    def set_auth(cls, inv_user, inv_pass):
        cls.auth = HTTPBasicAuth(inv_user, inv_pass)

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


@basic_auth
def make_inv_request(method: str, path: str, **kwargs) -> requests.Response:
    """
    Helper function for calling APIs

    Args:
        method: method used for calling the API
        path: API path on top of base URL

    Returns:
        Requests Response
    """
    url = BASE_URL + "/api" + path
    verify = not DEBUG  # turning off ssl verification when running in debug mode
    response = requests.request(method=method, url=url, verify=verify, **kwargs)
    return response


def get_locations():
    keys = ["pk", "name"]
    response = make_inv_request(method="GET", path="/stock/location/")
    return parse_json(data=response.json(), keys=keys)


def get_stock():
    keys = ["pk", "serial", "customer", "location"]
    response = make_inv_request(method="GET", path="/stock/")
    return parse_json(data=response.json(), keys=keys)


def get_customers():
    keys = ["pk", "name", "email"]
    response = make_inv_request(method="GET", path="/company/")
    return parse_json(data=response.json(), keys=keys)


def parse_json(data: dict, keys):
    """
    Returns list of dicts with only selected keys
    """
    return [{key: i.get(key) for key in keys} for i in data]


def assign_stock(item_ids: list, name_id: int):
    """
    Assign stock items to a customer.

    Args:
        item_ids: List of item primary keys to assign
        name_id: Customer primary key

    Raises:
        ValueError: If items are not in stock
        requests.HTTPError: For other HTTP errors
    """
    json = {"items": [{"item": item_id} for item_id in item_ids], "customer": name_id}
    response = make_inv_request(method="POST", path="/stock/assign/", json=json)
    if response.status_code == 400:
        try:
            error_data = response.json()
            if error_data.get("items", [{}])[0].get("pk") == "Item must be in stock":
                raise ValueError("Item must be in stock")
        except (KeyError, IndexError):
            pass
    response.raise_for_status()


def return_stock(item_ids: list, location_id: int):
    """
    Return stock items to a location.

    Args:
        item_ids: List of item primary keys to return
        location_id: Location primary key

    Raises:
        ValueError: If items are already in stock
        requests.HTTPError: For other HTTP errors
    """
    json = {
        "items": [{"pk": item_id, "quantity": "1"} for item_id in item_ids],
        "location": location_id,
        "merge": True,
    }
    response = make_inv_request(method="POST", path="/stock/return/", json=json)
    if response.status_code == 400:
        try:
            response_data = response.json()
            pk_value = response_data.get("items", [{}])[0].get("pk")
            if isinstance(pk_value, list) and "Stock item is already in stock" in pk_value:
                raise ValueError("Stock item is already in stock")
        except (KeyError, IndexError):
            pass
    response.raise_for_status()


def add_customer(name: str, email: str):
    """
    Adds customers to a location.

    Args:
        item_ids: List of item primary keys to return
        location_id: Location primary key

    Raises:
        ValueError: If items are already in stock
        requests.HTTPError: For other HTTP errors
    """
    json = {
        "name": name,
        "email": email,
        "currency": "USD",
        "active": True,
        "is_customer": True,
        "is_manufacturer": False,
        "is_supplier": False,
    }
    response = make_inv_request(method="POST", path="/company/", json=json)
    response.raise_for_status()
