from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User
from sqlalchemy.exc import IntegrityError
from forms import UserForm, LoginForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///eat_clean_user"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fvkhghi265grfgef5'
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

@app.route('/')
def home_page():
    """Home page."""

    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register_user():
    form = UserForm()
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        new_user = User.register(username, email, password)

        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please choose another username')
            return render_template('register.html', form=form)

        session['user_id'] = new_user.id
        flash('Welcome! Succesfully Created Your Account! ', "success")
        return redirect('/')
    
    return render_template('register.html', form=form)


@app.route('/login', methods=["GET","POST"])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user: 
            flash(f"Welcome back, {user.username}! ", "primary")
            session['user_id'] = user.id
            return redirect('/')
        else:
            form.username.errors = ["Invalid username/password."]

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("Goodbye, see you next meal!", "info")
    return redirect('/')