import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///noms.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    return(render_template("index.html"))

@app.route("/recipes", methods=["GET", "POST"])
@login_required
def find_recipes():
    # If user reaches route via POST
    if request.method == "POST":
        
        # Get list of ingredients from form
        ingredients = request.form.getlist("ingredient")

        # Get all recipes from SQL database
        all_recipes = db.execute("SELECT recipe_name FROM recipes")

        # Make copy of all recipes
        copy = all_recipes.copy()

        # Iterate through each recipe and get ingredients in each recipe
        for recipe in copy:
            recipe_ingredients = db.execute("SELECT ingredient_name FROM ingredients WHERE id IN (SELECT ingredient_id FROM cooking_ingredients WHERE recipe_id = (SELECT id FROM recipes WHERE recipe_name = ?))", recipe['recipe_name'])
            
            # Iterate through each ingredient in the recipe
            for ingredient in recipe_ingredients:
                
                # Check whether each ingredient in the recipe has been checked off by user
                if ingredient['ingredient_name'] not in ingredients:

                    # If ingredient has not been selected, remove recipe from all recipes if list not empty
                    if recipe in all_recipes:
                        all_recipes.remove(recipe)

        # Render template to display recipes with owned ingredients
        return(render_template("cook.html", ingredients=ingredients, recipes=all_recipes))
    
    # If user reaches route via GET
    else:
        
        # Select all ingredients from SQL database
        all_ingredients_raw = db.execute("SELECT ingredient_name FROM ingredients")
        
        # Initialize empty list
        all_ingredients = []

        # Iterate through each item in raw ingredient list
        for ingredient in all_ingredients_raw:
            
            # Add each ingredient to ingredients list, extracting value from dictionary
            all_ingredients.append(ingredient['ingredient_name'])

        # Render recipes template, passing ingredients
        return(render_template("recipes.html", ingredients=all_ingredients))

@app.route("/favorites", methods=["GET", "POST"])
@login_required
def favorites():
    return(redirect("/"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    # When submitted via POST, check for errors and insert new user into users table
    if request.method == "POST":
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        # If fields are left blank, return error
        if not new_username or not new_password or not confirmation:
            return apology("must fill out all fields", 400)
        
        # If password doesn't match confirmation, return error
        if new_password != confirmation:
            return apology("password confirmation does not match password", 400)

        # Hash password for security
        password_hash = generate_password_hash(new_password)
        
        # Insert user into SQL table
        try:
            id = db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", new_username, password_hash)        
        except ValueError:
            return apology("username already taken", 400)

        # Log user in
        session["user_id"] = id
        return redirect("/")

    # When requested via GET, display registration form
    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
