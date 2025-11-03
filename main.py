from flask import Flask, render_template, request
from inventree_calls import get_names

token = "token inv-b0d001f86ec7dca3bb8b520965219503bba7baf0-20251103"
base_url = "http://inventree.localhost"
app = Flask(__name__)


# add validation
@app.route("/")
def index():
    names = get_names(base_url, token)
    return render_template("index.j2", names=names)


# to move location http://inventree.localhost/api/stock/transfer/
# add validation for names and serials since that can be edited from FE and are part of post request
@app.route("/manage_device", methods=["POST"])
def manage_device():
    name = request.form["name"]
    serials = request.form["serials"]
    if request.form.get("action") == "Check In":
        action = "check_in"
    elif request.form.get("action") == "Check Out":
        action = "check_out"
    else:
        raise Exception
    print(name, serials, action)
    return render_template("success.j2")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
