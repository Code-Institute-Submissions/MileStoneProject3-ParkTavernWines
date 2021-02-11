import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from bson.objectid import ObjectId
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
    wine_list = mongo.db.wine_list.find()
    return render_template("wines.html", wine_list=wine_list)



# Building NavBar with Flask


nav = Nav(app)


nav.register_element("navbar", Navbar(
    "thenav",
    View("Home Page", "index"),
    View("Register", "index"),
    View("Log In", "index")))


@app.route("/")
def index():
    return render_template("base.html")

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
