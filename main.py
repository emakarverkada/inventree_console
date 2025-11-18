import os
from flask import Flask, render_template, flash, redirect, url_for, request

from inventree_calls import (
    get_names,
    get_locations,
    get_stock,
    assign_stock,
    return_stock,
)
from forms import InvTrackingForm

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")


@app.route("/", methods=["GET", "POST"])
def index():
    # Only bind form data on POST requests, create fresh form on GET
    form = InvTrackingForm(request.form if request.method == "POST" else None)
    form.name.choices = get_names()
    form.location.choices = get_locations()

    if form.validate_on_submit():
        name_id = form.name.data
        location_id = form.location.data

        # Get cleaned serials from form (validation already handled by form)
        serials = form.get_cleaned_serials()

        try:
            stock = get_stock()
        except Exception as e:
            flash(f"Error fetching stock data: {str(e)}", "error")
            return redirect(url_for("index"))

        away_items = []
        in_stock_items = []
        wrong_customer_items = []
        correct_customer_items = []

        for serial in serials:
            result = next((t for t in stock if t["serial"] == serial), None)
            if result is None:
                flash(f"Serial '{serial}' not found in system", "error")
                return redirect(url_for("index"))

            if result["customer"] is None:
                in_stock_items.append(result["pk"])
            else:
                away_items.append(result["pk"])
                # Check if item is checked out to a different customer
                if form.check_out.data and result["customer"] != name_id:
                    wrong_customer_items.append(result["pk"])
                elif form.check_out.data and result["customer"] == name_id:
                    correct_customer_items.append(result["pk"])

        if form.check_in.data:
            if away_items:
                try:
                    return_stock(away_items, location_id)
                    flash("You successfully returned items to the lab")
                except Exception as e:
                    flash(f"Error returning items: {str(e)}", "error")
                return redirect(url_for("index"))
            else:
                flash("No items to return")
                return redirect(url_for("index"))

        elif form.check_out.data:
            items_to_checkout = []
            messages = []
            tse_message = None

            # If there are items checked out to wrong customer, return them to stock first
            if wrong_customer_items:
                try:
                    # Need location_id to return items - use the location from the form
                    return_stock(wrong_customer_items, location_id)
                    # After returning, add them to the checkout list
                    items_to_checkout.extend(wrong_customer_items)
                    tse_message = f"Returned {len(wrong_customer_items)} item(s) from another TSE to lab"
                except Exception as e:
                    flash(f"Error returning items to stock: {str(e)}", "error")
                    return redirect(url_for("index"))

            # Add items that were already in stock
            items_to_checkout.extend(in_stock_items)

            # Items already checked out to correct customer don't need action
            if correct_customer_items:
                messages.append(f"{len(correct_customer_items)} item(s) already checked out")

            if items_to_checkout:
                try:
                    assign_stock(items_to_checkout, name_id)
                    # Build message with TSE message first if it exists
                    main_message = f"You successfully checked out {len(items_to_checkout)} item(s)"
                    if tse_message:
                        if messages:
                            flash(f"{tse_message}. {main_message}. {' '.join(messages)}")
                        else:
                            flash(f"{tse_message}. {main_message}")
                    elif messages:
                        flash(f"{main_message}. {' '.join(messages)}")
                    else:
                        flash("You successfully checked out items out of the lab")
                    return redirect(url_for("index"))
                except Exception as e:
                    flash(f"Error checking out items: {str(e)}", "error")
                    return redirect(url_for("index"))
            elif correct_customer_items:
                # Only items already checked out to correct customer
                flash(f"All {len(correct_customer_items)} item(s) are already checked out")
                return redirect(url_for("index"))
            else:
                flash("No items to check out")
                return redirect(url_for("index"))
    return render_template("index.j2", form=form)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
