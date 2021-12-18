import os
from flask import Flask, render_template, redirect, session, flash, request, jsonify, g
from models import connect_db, db, User, Ingredient, Meal
from sqlalchemy.exc import IntegrityError
from forms import UserForm, LoginForm, UserEditForm
import requests
from helper import do_logout, add_ingredients_from_api_response

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
    # query = request.args.get('query', "")
    # cuisine = request.args.get('cuisine', "")
    # diet = request.args.get('diet', "")
    # offset = request.args.get('offset')
    # number = 8
    
    query = request.args.get('query',"")
  
    res = requests.get(f"{BASE_URL}/food/ingredients/search", params={ "apiKey": API_KEY, "query":query})
    data = res.json()
    
   
    if data.get('result') == 0:
        flash("Sorry, search limit reached!", "warning")
        render_template("/index.html")
    
    # path = f"/search?query={query}&cuisine={cuisine}&diet={diet}"
    ingredients = data['results']
    if g.user:
        ingredient_ids = [r['id'] for r in ingredients]
    else:
        ingredient_ids = []

    meals = [m['id'] for m in ingredients if m['id'] in ingredient_ids]

    ### add favorite function here
    return render_template("/foods/search.html", ingredients=ingredients, ingredient_ids=ingredient_ids, meals=meals)



@app.route("/meals")
def meal_page():
    """Show User's meal."""
    if not g.user:
        flash('You must be logged in first','danger')
        return redirect("/login")

    ingredient_ids = [r['id'] for r in g.user.ingredients]

    return render_template("/foods/meals.html", ingredient_ids=ingredient_ids)

@app.route("/api/meal/<int:id>", methods=["POST"])
def add_meal(id):
    """Add to meals."""
    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")

    ingredient = Ingredient.query.filter_by(id=id).first()
    if not ingredient:
        res = requests.get(f"{BASE_URL}/food/ingredients/{id}/information", params={ "apiKey": API_KEY })
        data = res.json()
        print(data)
        ingredient = add_ingredients_from_api_response(data)

        g.user.ingredients.append(ingredient)
        db.session.commit()
    else:
        g.user.ingredients.append(ingredient)
        db.session.commit()

    return jsonify(ingredient=ingredient.serialize())



# def add_ingredients_from_api_response(ingredient):
#     """Add ingredients to the meal."""

#     id = ingredient.get('id', None)
#     name = ingredient.get('name', None)

#     meal = Ingredient(id=id, name=name)
#     try:
#         db.session.add(meal)
#         db.session.commit()

#     except Exception:
#         db.session.rollback()
#         print("Exception", str(Exception))
#         return "Sorry, Error, Please try again later", str(Exception)
#     return meal



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

if __name__ == '__main__':
    app.run()