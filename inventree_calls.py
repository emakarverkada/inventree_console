import os
import requests

token = os.getenv("INVENTREE_TOKEN", "token inv-b0d001f86ec7dca3bb8b520965219503bba7baf0-20251103")
base_url = os.getenv("INVENTREE_BASE_URL", "http://inventree.localhost")


def inv_get_call(path: str, key_names: list):
    """
    Calls Inventree API and returns JSON data.

    Args:
        path: API endpoint path
        key_names: List of keys to extract (currently unused but kept for compatibility)

    Returns:
        JSON response data from the API
    """
    headers = {"Authorization": token}
    url = base_url + path
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_names():
    keys = ["pk", "name"]
    data = inv_get_call("/api/company/", keys)
    return [(i["pk"], i["name"]) for i in data]


def get_locations():
    keys = ["pk", "name"]
    data = inv_get_call("/api/stock/location/", keys)
    return [(i["pk"], i["name"]) for i in data]


def get_stock():
    keys = ["pk", "serial", "customer", "location"]
    data = inv_get_call("/api/stock/", keys)
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
    headers = {"Authorization": token}
    url = base_url + "/api/stock/assign/"
    body = {"items": [{"item": item_id} for item_id in item_ids], "customer": name_id}
    response = requests.post(url, headers=headers, json=body)
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
    headers = {"Authorization": token}
    url = base_url + "/api/stock/return/"
    body = {
        "items": [{"pk": item_id, "quantity": "1"} for item_id in item_ids],
        "location": location_id,
        "merge": True,
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 400:
        try:
            response_data = response.json()
            pk_value = response_data.get("items", [{}])[0].get("pk")
            if isinstance(pk_value, list) and "Stock item is already in stock" in pk_value:
                raise ValueError("Stock item is already in stock")
        except (KeyError, IndexError):
            pass
    response.raise_for_status()
