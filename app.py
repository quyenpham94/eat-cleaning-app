import os
from flask import Flask, render_template, redirect, session, flash, request, jsonify, g
from models import connect_db, db, User, Ingredient, Meal, Recipe
from sqlalchemy.exc import IntegrityError
from forms import UserForm, LoginForm, UserEditForm
import requests
from helper import do_logout, add_ingredients_from_api_response, add_recipe_from_api_response, diets, maxFats, maxCalorieses

CURR_USER_KEY = "user_id"
 
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', "postgresql:///eat_clean_user")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'is a secret')
app.config['SQLALCHEMY_ECHO'] = False



BASE_URL = "https://api.spoonacular.com/"
API_KEY = ""


connect_db(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, and curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

########## signup, login, logout ################


@app.route('/register', methods=['GET','POST'])
def register_user():

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = UserForm()
     
    if form.validate_on_submit():
        try:
            user = User.register(
                username = form.username.data,
                email = form.email.data,
                password = form.password.data
            )
            db.session.commit()

        except IntegrityError:
            flash('Username taken. Please choose another username','danger')
            return render_template('users/register.html', form=form)

        do_login(user)
        flash('Welcome! Succesfully Created Your Account! ', "success")
        return redirect('/')
    else:
        return render_template('users/register.html', form=form)


@app.route('/login', methods=["GET","POST"])
def login_user():
    """Handle login of user."""

    form = LoginForm()

    if form.validate_on_submit():

        user = User.authenticate(form.username.data, 
                                 form.password.data)
        if user: 
            do_login(user)
            flash(f"Welcome back, {user.username}! ", "success")
            return redirect('/')
        else:
            form.username.errors = ["Invalid username/password.","danger"]

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout_user():
    """Handle logout of user."""

    do_logout()
    flash("Goodbye, see you next meal!", "success")
    return redirect('/')

@app.route("/users/<int:user_id>")
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)
    return render_template('users/show.html', user=user)

@app.route("/users/<int:user_id>/update", methods=["GET","POST"])
def update_profile(user_id):
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.","danger")
        return redirect("/")

    user = User.query.get(user_id)
    form = UserEditForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash(f"You have updated your account!", "success")
        return redirect(f"/users/{user.id}")
        
    return render_template('users/edit.html', form=form, user_id=user.id)

@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.","danger")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()
    session.pop(CURR_USER_KEY)
    flash(f"{g.user.username}'s account has been deleted!", 'secondary')
    return redirect('/')



################### eat-cleaning-function #############
@app.route('/')
def home_page():
    """Home page."""
    
    return render_template('index.html')

@app.route("/search")
def search_ingredient():

    query = request.args.get('query',"")
  
    res = requests.get(f"{BASE_URL}/food/ingredients/search", params={ "apiKey": API_KEY, "query":query})
    data = res.json()
    
   
    if data.get('result') == 0:
        flash("Sorry, search limit reached!", "warning")
        render_template("/index.html")
    
    ingredients = data['results']
    if g.user:
        ingredient_ids = [r['id'] for r in ingredients]
    else:
        ingredient_ids = []

    meals = [m['id'] for m in ingredients if m['id'] in ingredient_ids]

    ### add favorite function here
    return render_template("/foods/search.html", ingredients=ingredients, ingredient_ids=ingredient_ids, meals=meals)

@app.route("/ingredients/<int:id>")
def show_ingredient(id):
    res1 = requests.get(f"{BASE_URL}/recipes/{id}/nutritionWidget.json", params={ "apiKey": API_KEY })
    data1 = res1.json()
    res2 = requests.get(f"{BASE_URL}/food/ingredients/{id}/information", params={ "apiKey": API_KEY, "amount":1 })
    data2 = res2.json()
    name = data2['name']
    return render_template("foods/ingredients.html", nutrition=data1, name=name)

@app.route("/meals")
def meal_page():
    """Show User's meal."""
    
    if not g.user:
        flash('You must be logged in first','danger')
        return redirect("/login")
    
    user_response = g.user.ingredients
    ingredient_ids = [r.id for r in user_response]

    return render_template("/foods/meals.html", ingredient_ids=ingredient_ids)


@app.route("/api/meal/<int:id>", methods=["POST"])
def add_meal(id):
    """Add to meals."""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")

    ingredient = Ingredient.query.filter_by(id=id).first()
    if not ingredient:
        res = requests.get(f"{BASE_URL}/food/ingredients/{id}/information", params={ "apiKey": API_KEY, "amount":1 })
        data = res.json()
        
        ingredient = add_ingredients_from_api_response(data)

        g.user.ingredients.append(ingredient)
        db.session.commit()
    else:
        g.user.ingredients.append(ingredient)
        db.session.commit()

    return jsonify(ingredient=ingredient.serialize())


@app.route("/random")
def show_recipes():
    """Show random recipes auto populated"""
    res = requests.get(f"{BASE_URL}/recipes/random", params={ "apiKey": API_KEY, "number": 9 })
    data = res.json()

    if data.get('recipes') == 0:
        flash("Sorry, search limit reached!", "warning")
        return render_template("index.html")
    recipes = data['recipes']

    if g.user:
        recipe_ids = [r.id for r in g.user.recipes]
    else:
        recipe_ids = []
    favorites = [f['id'] for f in recipes if f['id'] in recipe_ids]
    return render_template("/foods/random.html", recipes=recipes, recipe_ids=recipe_ids, favorites=favorites, diets=diets, maxCalorieses=maxCalorieses, maxFats=maxFats)


@app.route("/refine")
def search_recipe():
    """Inside random recipes show refine search by diets and nutritions"""
    # query = request.args.get('query', "")
    
    diet = request.args.get('diet', "")
    maxFat = request.args.get('maxFat',"")
    maxCalories = request.args.get('maxCalories', "")
    offset = request.args.get('offset')
    number = 9
   
    
    res = requests.get(f"{BASE_URL}/recipes/complexSearch", params={ "apiKey": API_KEY, "diet": diet, "maxFat": maxFat, "maxCalories": maxCalories, "number": number, "offset": offset})
    data = res.json()
   
    if data.get('result') == 0:
        flash("Sorry, search limit reached!", "warning")
        render_template("/foods/random.html")
    
    path = f"/refine?maxFat={maxFat}&maxCalories={maxCalories}&diet={diet}"
    recipes = data['results']
    if g.user:
        recipe_ids = [r.id for r in g.user.recipes]
    else:
        recipe_ids = []
    favorites = [f['id'] for f in recipes if f['id'] in recipe_ids]
    return render_template("/foods/recipes.html", diets=diets, maxFats=maxFats, maxCalorieses=maxCalorieses, recipes=recipes, recipe_ids=recipe_ids, favorites=favorites, url=path, offset=offset)




@app.route("/recipes/<int:id>")
def show_recipe(id):
    res = requests.get(f"{BASE_URL}/recipes/{id}/information", params={ "apiKey": API_KEY, "includeNutrition": False })
    data = res.json()
    return render_template("foods/details.html", recipes=data)

# ----------------------------------------

@app.route("/favorites")
def show_favorites():
    if not g.user:
        flash("You must be logged in to view favorites", "danger")
        return redirect("/login")
    
    user_res = g.user.recipes
    recipe_ids = [r.id for r in user_res]

    return render_template("foods/favorites.html", recipe_ids=recipe_ids)



@app.route("/api/favorite/<int:id>", methods=["POST"])
def add_favorite(id):
    """Add to favorites"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    recipe = Recipe.query.filter_by(id=id).first()
    if not recipe:
        res = requests.get(f"{BASE_URL}/recipes/{id}/information", params={ "apiKey": API_KEY, "includeNutrition": True })
        data = res.json()
        recipe = add_recipe_from_api_response(data)
        


        g.user.recipes.append(recipe)
        db.session.commit()
    else:
        g.user.recipes.append(recipe)
        db.session.commit()
        
    return jsonify(recipe=recipe.serialize())

@app.route("/api/favorite/<int:id>", methods=["DELETE"])
def delete_favorite(id):
    """Unfavorite a recipe."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    recipe = Recipe.query.filter_by(id=id).first()

    try:
        db.session.delete(recipe)
        db.session.commit()
        
    except Exception as e:
        print("Error", e)
        return jsonify(errors=str(e))
    return jsonify(recipe=recipe.serialize())

@app.errorhandler(404)
def error_page(error):
    """Show 404 ERROR page if page NOT FOUND"""
    return render_template("error.html"), 404


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers["Cache-Control"] = "public, max-age=0"
    return req

