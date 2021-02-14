import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_wine_list")
def get_winelist():
    wine_list = list(mongo.db.wine_list.find())
    return render_template("wines.html", wine_list=wine_list)


@app.route("/wineinfo/<wine_id>", methods=["GET", "POST"])
def wineinfo(wine_id):
    wine = mongo.db.wine_list.find_one({"_id": ObjectId(wine_id)})
    wine_list = mongo.db.wine_list.find()
    return render_template("wineinfo.html", wine=wine, wine_list=wine_list)


# Building NavBar with Flask


nav = Nav(app)


nav.register_element("navbar", Navbar(
    "thenav",
    View("Home Page", "index"),
    View("Register", "register"),
    View("Log In", "login")))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Oops get more origional!")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
          {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                 existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                return redirect(url_for(
                    "wines", username=session["user"]))
            else:
                flash("Whoops too much wine, Username/Password is incorrect")
                return redirect(url_for("login"))
        else:
            flash("Sorry, Username does not exist")
            return redirect(url_for("login"))
    return render_template('login.html')


@app.route("/")
def index():
    return render_template("base.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
