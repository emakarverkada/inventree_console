from flask import Flask, render_template, request

app = Flask(__name__)


app = Flask(__name__)


@app.route("/")
def index():
    names = ["Erin Makarova", "Sander Solsvik", "Ethan McLeod", "Benjamin Balko"]
    return render_template("index.j2", names=names)


@app.route("/manage_device", methods=["POST"])
def manage_device():
    name = request.form["name"]
    serials = request.form["serials"]
    print(name, serials)
    return render_template("success.j2")


def get_names():
    pass


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
