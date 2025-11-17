from flask import Flask, render_template, flash, redirect, url_for
from flask_caching import Cache
import regex as re
import requests.exceptions
from time import sleep

from inventree_calls import *
from forms import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"
cache = Cache()


@app.route("/", methods=["GET", "POST"])
def index():
    form = InvTrackingForm()
    # TODO Fix how data is given from api call so it can be reused and validated
    form.name.choices = get_names()
    form.location.choices = get_locations()

    if form.validate_on_submit():
        name_id = form.name.data
        location_id = form.location.data
        serials = str(form.serials.data)
        serials = re.split(r"[;,\s]+", serials)

        stock = get_stock()
        away_items = []
        in_stock_items = []
        for serial in serials:
            result = next((t for t in stock if t["serial"] == serial), None)
            if result == None:
                raise Exception("Serial:", serial, "Not found in system")
            else:
                if result["customer"] == None:
                    in_stock_items.append(result["pk"])
                else:
                    away_items.append(result["pk"])

        if form.check_in.data:
            print(away_items, location_id)
            if away_items:
                return_stock(away_items, location_id)
                flash("You successfully returned items to the lab")
                return redirect(url_for("index"))
            else:
                flash("No items to return")
                return redirect(url_for("index"))

        elif form.check_out.data:
            if in_stock_items:
                assign_stock(in_stock_items, name_id)
                flash("You successfully checked out items out of the lab")
                return redirect(url_for("index"))
            else:
                flash("No items to check out")
                return redirect(url_for("index"))
    return render_template("index.j2", form=form)


# 7JEN-AN96-M4YA
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
