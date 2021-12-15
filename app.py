import os
from flask import Flask, render_template, redirect, session, flash, request, jsonify, g
from models import connect_db, db, User, Meal
from sqlalchemy.exc import IntegrityError
from forms import UserForm, LoginForm, MealForm, UserEditForm
import requests
from helpers import get_ingredients_from_api_response

CURR_USER_KEY = "user_id"
 
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', "postgresql:///eat_clean_user")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fvkhghi265grfgef5'
app.config['SQLALCHEMY_ECHO'] = False



BASE_URL = "https://api.spoonacular.com/"
API_KEY = "7661a2feb8364ca09a645444d3ed9189"


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

@app.route('/')
def home_page():
    """Home page."""
    
    return render_template('index.html', user=user)


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
################### eat-cleaning-function #############

# @app.route('/meals')
# def meal_page():
#     if "user_id" not in session:
#         flash("Please login first!", "danger")
#         return redirect('/')
#     formuser = UserForm()
#     form = MealForm()
#     query = request.args.get('query', "")
#     cuisine = request.args.get('cuisine', "")
#     diet = request.args.get('diet', "")
#     offset = request.args.get('offset')
#     number = 8
#     all_ingredients = Meal.query.all()
#     if request.args:
        
#         res = requests.get(f"{BASE_URL}/recipes/complexSearch", params ={ "apiKey": API_KEY, "diet": diet, "cuisine": cuisine, "query": query, "number": number, "offset": offset })
#         data = res.json()
#         if data['results'] == '0':
#             flash("Sorry, search limit reached", "warning")
#             return render_template('meals.html', form=form)
#         else:
#             ingredients = get_ingredients_from_api_response(data)
#             return render_template('meals.html', form=form, ingredients=ingredients)
#     try:
#         transaction.commit()
#     except e:
#         session.rollback()
#         print str(e)
#     return redirect('/meals')