import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

# Configuring

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_wine_list")
# Get the wine list and iterate through
def get_winelist():
    wine_list = list(mongo.db.wine_list.find())
    return render_template("wines.html", wine_list=wine_list)


@app.route("/wineinfo/<wine_id>", methods=["GET", "POST"])
# Find wine by id so when clicked on one page it only shows the wine clicked
def wineinfo(wine_id):
    wine = mongo.db.wine_list.find_one({"_id": ObjectId(wine_id)})
    wine_list = mongo.db.wine_list.find()
    return render_template("wineinfo.html", wine=wine, wine_list=wine_list)


@app.route("/register", methods=["GET", "POST"])
def register():
    # make a register page
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
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # making the login page
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
          {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                 existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Success...Browse our winessss")
                return redirect(url_for(
                    "profile", username=session["user"]))

            else:
                flash("Whoops too much wine, Username/Password is incorrect")
                return redirect(url_for("login"))
        else:
            flash("Are you new? Username doesn't exist")
            return redirect(url_for("register"))
    return render_template('login.html')


@app.route("/logout")
def logout():
    # allow the user to logout
    flash("Miss You Already, enjoy your wine....sip sip sip away")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/addreview/<wine_id>", methods=["GET", "POST"])
def addreview(wine_id):
    # allows to adda review of the wine
    if session.get("user"):
        if request.method == "POST":
            review = {
                "wine_id": wine_id,
                "comment": request.form.get("comment"),
                "user_id": session["user"],
            }
            mongo.db.reviews.insert_one(review)
            flash("Review Successfully Added")
            wine = mongo.db.wine_list.find_one({'_id': ObjectId(wine_id)})
            return redirect(url_for("wineinfo", wine_id=wine_id))
        else:
            wine = mongo.db.wine_list.find_one({'_id': ObjectId(wine_id)})
            return render_template("addreview.html", wine=wine)
    flash("You Must Register/Log In To Add A Review")
    return redirect(url_for("register"))


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # giving the user a profile page
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if session["user"]:
        wines = []
        if session["user"] == "admin":
            reviews = list(mongo.db.reviews.find({}))
        else:
            reviews = list(mongo.db.reviews.find({'user_id': session['user']}))
    return render_template(
        "profile.html", username=username,
        reviews=reviews, wines=wines)


@app.route("/")
def index():
    # base of html templates
    return render_template("base.html")

# initialising the app


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
