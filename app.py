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
    
    # Get random recipe for button on website
    random_recipe = db.execute("SELECT url FROM recipes ORDER BY RANDOM()")[0]

    # Get random restaurant for button on website
    random_restaurant = db.execute("SELECT url FROM restaurants ORDER BY RANDOM()")[0]

    # Return index template
    return(render_template("index.html", random_recipe=random_recipe, random_restaurant=random_restaurant))

@app.route("/restaurants", methods=["GET", "POST"])
@login_required
def find_restaurants():
    
    # If user reaches route via POST
    if request.method == "POST":
        
        # Get value of cuisine selected in form
        cuisine = request.form.get("cuisine")
        
        # If user selects any cuisine, select all restaurants
        if cuisine == "Any cuisine":
            restaurants = db.execute("SELECT * FROM restaurants")
        
        # If user selects certain cuisine, select restaurants with selected cuisine type
        else:
            restaurants = db.execute("SELECT * FROM restaurants WHERE cuisine = ?", cuisine)
        
        # Render template showing all restaurant choices
        return(render_template("restaurant_choice.html", restaurants=restaurants))
    
    # If user reaches route via GET
    else:
        
        # Select each distinct cuisine from restaurants table
        cuisines = db.execute("SELECT DISTINCT cuisine FROM restaurants")
        
        # Render template showing form with all cuisines
        return(render_template("restaurants.html", cuisines=cuisines))

@app.route("/recipes", methods=["GET", "POST"])
@login_required
def find_recipes():
    # If user reaches route via POST
    if request.method == "POST":
        
        # Get list of ingredients from form
        ingredients = request.form.getlist("ingredient")

        # Get all recipes from SQL database
        all_recipes = db.execute("SELECT recipe_name, url FROM recipes")

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

        if all_recipes == []:
            return(apology("No recipes found. Try adding more ingredients!"))

        # Render template to display recipes with owned ingredients
        return(render_template("cook.html", ingredients=ingredients, recipes=all_recipes))
    
    # If user reaches route via GET
    else:
        
        # Select all ingredients from SQL database
        all_ingredients = db.execute("SELECT ingredient_name FROM ingredients")
        
        # Render recipes template, passing ingredients
        return(render_template("recipes.html", ingredients=all_ingredients))

@app.route("/favorites")
@login_required
def favorites():
    # Get user id
    user_id = session["user_id"]

    # Select all recipe names and links that the user has favorited 
    favorites = db.execute("SELECT recipe_name, url FROM recipes WHERE id IN (SELECT DISTINCT recipe_id FROM favorites WHERE user_id = ?)", user_id)
    
    # Render template with table of favorites
    return(render_template("favorites.html", favorites=favorites))

@app.route("/add_favorites", methods=["GET", "POST"])
@login_required
def add_favorites():
    
    # If user reaches route via POST
    if request.method == "POST":
        
        # Get user id
        user_id = session["user_id"]
        
        # Get value from form
        favorite = request.form.get("add-favorites")
        
        # Select id of recipe that user wants to add to their favorites
        favorite_id = db.execute("SELECT id FROM recipes WHERE recipe_name = ?", favorite)

        # Insert id into favorites table along with user's id
        db.execute("INSERT INTO favorites ('user_id', 'recipe_id') VALUES (?, ?)", user_id, favorite_id[0]['id'])

        # Redirect to favorites page, updating with new added favorite
        return(redirect("/favorites"))

    # If user reaches route via GET
    else:

        # Display form with all recipes
        all_recipes = db.execute("SELECT recipe_name FROM recipes")

        # Render template showing dropdown of every recipe
        return(render_template("add_favorites.html", recipes=all_recipes))

@app.route("/delete_favorites", methods=["GET", "POST"])
@login_required
def delete_favorites():

    # Get user id
    user_id = session["user_id"]

    # If user reaches route via POST
    if request.method == "POST":

        # Get value from form
        delete_name = request.form.get("delete-favorites")

        # Select id of recipe that user wants to delete from favorites and perform SQL query to delete
        delete_id = db.execute("SELECT id FROM recipes WHERE recipe_name = ?", delete_name)
        db.execute("DELETE FROM favorites WHERE recipe_id = ?", delete_id[0]['id'])
        
        # Redirect to favorites
        return(redirect("/favorites"))
    
    # If user reaches route via GET
    else:
        
        # Select all recipes that user has favorited
        favorites = db.execute("SELECT recipe_name FROM recipes WHERE id IN (SELECT recipe_id FROM favorites WHERE user_id = ?)", user_id)
        
        # Render template showing all favorites of user
        return(render_template("delete_favorites.html", favorites=favorites))

@app.route("/huds")
@login_required
def huds():
    return(redirect("https://dining.harvard.edu/campus-dining/undergraduate-dining/weeks-menu"))

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
