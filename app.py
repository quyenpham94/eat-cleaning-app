from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db
from sqlalchemy.exc import IntegrityError


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