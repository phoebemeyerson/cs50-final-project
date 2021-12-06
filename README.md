# NOMS: The Food Website for Harvard Students 

NOMS is a website for Harvard students to explore easy recipes from ingredients they already have in their pantry, navigate and explore the Harvard Square restaurant scene, and check out the weekly HUDS menu. 

Features: 
User can 
    register for an account and login/logut,
    search recipes from ingredients they already have through our database of simple recipes,
    save recipes they love to "Favorites" in their account (and remove them from "Favorites" if desired), 
    explore Harvard Sqaure restaurants by cuisine,
    and check out the HUDS weekly menu.

# Installation 

Using Visual Studio Code, open the cs50-final-project folder.
To render the website, in the command line terminal run: "flask run" and open the link generated in a browser. 
Finally, see "usuage" for a full explanation of the webste's capabilities.  

# Usage 

Using the "Register" tab in the top right corner, the user will be prompted to create an account with a username and password. 
The "Login" tab will prompt the user to input their username and password to begin their session within the website. 
The "Logout" tab will sign the user out of their session and redirect them to the "Login" page. 
The index page of our website:
    welcomes the user to NOMS, 
    when clicked, the "Show me a random recipe!" button redirects the user to a random recipe's (from our database) website,
    when clicked, the "Show me a random restaurant!" button redirects the user to a random restaurant's website,
    and the bottom explains the capabilities of our website with hyperlinks to direct the user to its features (recipes, restaurants, favorites, and the HUDS menu).
The "Recipes" feature of our website: 
    prompts the user to select ingredients (from our database) that they own in order to receive a list of recipe(s) that include only the ingredients they have inputted. 
    If no recipes exist, an apology is rendered and the user is advised to select more ingredients. 
The "Restaurants" feature of our website: 
    allows the user to search through our databse of Harvard Square resturants by cuisine and returns a list of restaurants (hyperlinked to the restaurant's website) and an image of the restaurant. 
The "Favorites" feature of our website: 
    displays the user's list of "Favorite" recipes (hyperlinked to the recipe's website) and has two features: 
        "add Favorites" allows the user to save  specific recipes (from our entire list of recipes) to his/her "Favorites" list, which allows for quick access to the hyperlinked recipe website, while 
        "remove Favorites" allows the user to remove a saved recipe from his/her list of saved "Favorites." 
The "Weekly HUDS" tab: 
    redirects the user to the HUDS weekly menu website. 

