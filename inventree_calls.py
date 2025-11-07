import requests as re

token = "token inv-b0d001f86ec7dca3bb8b520965219503bba7baf0-20251103"
base_url = "http://inventree.localhost"


def get_names():
    headers = {"Authorization": token}
    url = base_url + "/api/company/"
    names = {}
    response = re.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    for n in data:
        names[n["name"]] = n["pk"]
    return names


def get_stock():
    headers = {"Authorization": token}
    url = base_url + "/api/stock/"
    serials = {}
    response = re.get(url, headers=headers)
    response.raise_for_status()
    for n in response.json():
        serials[n["serial"]] = n["pk"]
    return serials


def get_locations():
    headers = {"Authorization": token}
    url = base_url + "/api/stock/location/tree/"
    names = {}
    response = re.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    for n in data:
        names[n["name"]] = n["pk"]
    return names


# TODO add error 400 check for when a device is already returned or checked out
def assign_stock(items_id: list, name_id: int):
    headers = {"Authorization": token}
    url = base_url + "/api/stock/assign/"
    body = {"items": [{"item": id} for id in items_id], "customer": name_id}
    response = re.post(url, headers=headers, json=body)
    response.raise_for_status()
    return None


# TODO add error 400 check for when a device is already returned or checked out
def return_stock(items_id: list, location_id: int):
    headers = {"Authorization": token}
    url = base_url + "/api/stock/return/"
    body = {"items": [{"pk": id, "quantity": "1"} for id in items_id], "location": location_id, "merge": True}
    response = re.post(url, headers=headers, json=body)
    response.raise_for_status()
    return None
