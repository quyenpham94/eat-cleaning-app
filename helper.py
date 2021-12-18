from flask import session
from models import db, User, Ingredient, Meal
import os

CURR_USER_KEY = "user_id"

def do_logout():
    """Logout User."""
    if CURR_USER_KEY in session:
        session.pop(CURR_USER_KEY)


def add_ingredients_from_api_response(ingredient):
    """Add ingredients to the meal."""

    id = ingredient.get('id', None)
    name = ingredient.get('name', None)

    meal = Ingredient(id=id, name=name)
    try:
        db.session.add(meal)
        db.session.commit()

    except Exception:
        db.session.rollback()
        print("Exception", str(Exception))
        return "Sorry, Error, Please try again later", str(Exception)
    return meal