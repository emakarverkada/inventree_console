from flask import Flask, render_template, flash, redirect, url_for, request
from flask_caching import Cache
import regex as re
import requests.exceptions
from time import sleep

from inventree_calls import *
from forms import InvTrackingForm

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

        # Collect all serial values from the FieldList
        serials = []
        for serial_field in form.serials:
            serial_value = serial_field.data.strip() if serial_field.data else ""
            if serial_value:
                serials.append(serial_value)

        # Remove duplicates while preserving order
        seen = set()
        serials = [s for s in serials if not (s in seen or seen.add(s))]

        # Check if we have any serials after filtering
        if not serials:
            flash("Please provide at least one valid serial number")
            return redirect(url_for("index"))

        stock = get_stock()
        away_items = []
        in_stock_items = []
        wrong_customer_items = []
        correct_customer_items = []

        for serial in serials:
            result = next((t for t in stock if t["serial"] == serial), None)
            if result == None:
                raise Exception("Serial:", serial, "Not found in system")
            else:
                if result["customer"] == None:
                    in_stock_items.append(result["pk"])
                else:
                    away_items.append(result["pk"])
                    # Check if item is checked out to a different customer
                    if form.check_out.data and result["customer"] != name_id:
                        wrong_customer_items.append(result["pk"])
                    elif form.check_out.data and result["customer"] == name_id:
                        correct_customer_items.append(result["pk"])

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
            items_to_checkout = []
            messages = []

            # If there are items checked out to wrong customer, return them to stock first
            if wrong_customer_items:
                try:
                    # Need location_id to return items - use the location from the form
                    return_stock(wrong_customer_items, location_id)
                    # After returning, add them to the checkout list
                    items_to_checkout.extend(wrong_customer_items)
                    messages.append(f"Returned {len(wrong_customer_items)} item(s) from another TSE to stock")
                except Exception as e:
                    flash(f"Error returning items to stock: {str(e)}")
                    return redirect(url_for("index"))

            # Add items that were already in stock
            items_to_checkout.extend(in_stock_items)

            # Items already checked out to correct customer don't need action
            if correct_customer_items:
                messages.append(f"{len(correct_customer_items)} item(s) already checked out")

            if items_to_checkout:
                try:
                    assign_stock(items_to_checkout, name_id)
                    if messages:
                        flash(f"You successfully checked out {len(items_to_checkout)} item(s). {' '.join(messages)}")
                    else:
                        flash("You successfully checked out items out of the lab")
                    return redirect(url_for("index"))
                except Exception as e:
                    flash(f"Error checking out items: {str(e)}")
                    return redirect(url_for("index"))
            elif correct_customer_items:
                # Only items already checked out to correct customer
                flash(f"All {len(correct_customer_items)} item(s) are already checked out")
                return redirect(url_for("index"))
            else:
                flash("No items to check out")
                return redirect(url_for("index"))
    return render_template("index.j2", form=form)


# 7JEN-AN96-M4YA
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
