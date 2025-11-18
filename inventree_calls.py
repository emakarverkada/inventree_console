import requests

token = "token inv-b0d001f86ec7dca3bb8b520965219503bba7baf0-20251103"
base_url = "http://inventree.localhost"


def inv_get_call(path: str, key_names: list):
    """
    Calls Inventree and returns a list of tuples in form of id, value
    """
    # It returns a list of tuples because this is how wtforms processes dropdown lists :)
    headers = {"Authorization": token}
    url = base_url + path
    # result = []
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    # for n in data:
    #    result.append(dict(map(n.get, key_names)))
    # result.sort(key=lambda tup: tup[1])
    return data


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


def assign_stock(items_id: list, name_id: int):
    headers = {"Authorization": token}
    url = base_url + "/api/stock/assign/"
    body = {"items": [{"item": id} for id in items_id], "customer": name_id}
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 400:
        try:
            if response.json()["items"][0]["pk"] == "Item must be in stock":
                raise Exception("Item must be in stock")
        except KeyError:
            response.raise_for_status()
    response.raise_for_status()
    return None


def return_stock(items_id: list, location_id: int):
    headers = {"Authorization": token}
    url = base_url + "/api/stock/return/"
    body = {"items": [{"pk": id, "quantity": "1"} for id in items_id], "location": location_id, "merge": True}
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 400:
        try:
            response_data = response.json()
            pk_value = response_data["items"][0].get("pk")
            if isinstance(pk_value, list) and "Stock item is already in stock" in pk_value:
                raise Exception("Stock item is already in stock")
        except (KeyError, IndexError):
            response.raise_for_status()
    response.raise_for_status()
    return None
