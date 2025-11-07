from flask import Flask, render_template, request
from flask_caching import Cache
from inventree_calls import *
import regex as re
import requests.exceptions

app = Flask(__name__)
cache = Cache()


# add validation
@app.route("/")
def index():
    try:
        customers = get_names()
        locations = get_locations()
        if customers == None:
            raise Exception("No users were returned by API")
        return render_template("index.j2", names=customers, locations=locations)
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Inventree - check server and network"


# add validation for names and serials since that can be edited from FE and are part of post request
@cache.cached(timeout=60)
@app.route("/manage_device", methods=["POST"])
def manage_device():
    name = eval(request.form["name"])
    name = {"name": name[0], "pk": int(name[1])}
    location = eval(request.form["location"])
    location = {"name": location[0], "pk": int(location[1])}
    serials = request.form["serials"]
    serials = re.split(r"[;,\s]+", serials)

    stock = get_stock()
    items_id = []
    for serial in serials:
        if serial not in stock:
            raise Exception("Serial:", serial, "Not found in system")
            # add rendering for it later
        else:
            print("Found serial", serial)
            items_id.append(int(stock[serial]))
            print(items_id)

    if request.form.get("action") == "Check In":
        print(name, serials)
        return_stock(items_id, location["pk"])
        return render_template("success.j2")
    elif request.form.get("action") == "Check Out":
        print(name, serials)
        assign_stock(items_id, name["pk"])
        return render_template("success.j2")
    else:
        raise Exception("Unknown Action")


# 7JEN-AN96-M4YA
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
