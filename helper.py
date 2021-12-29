from flask import session
from models import db, User, Ingredient, Meal, Recipe
import os

CURR_USER_KEY = "user_id"

def do_logout():
    """Logout User."""
    if CURR_USER_KEY in session:
        session.pop(CURR_USER_KEY)

diets = ['lacto vegetarian', 'ovo vegetarian', 'pescetarian', 'vegan', 'vegetarian', 'gluten free', 'ketogenic']

maxFats =  [10,20,30,50,60,70,80,90,100]

maxCalorieses = [50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800]

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



def add_recipe_from_api_response(recipe):
    """Add recipe to likes tables in the DB"""
    id = recipe.get('id', None)
    title = recipe.get('title', None)
    image = recipe.get('image', None)
    readyInMinutes = recipe.get('readyInMinutes', None)
    servings = recipe.get('servings', None)
    sourceName = recipe.get('sourceName', None)
    sourceUrl = recipe.get('sourceUrl', None)
    
    favorite = Recipe(id=id, title=title, image=image, readyInMinutes=readyInMinutes, sourceName=sourceName, sourceUrl=sourceUrl, servings=servings)
    try:
        db.session.add(favorite)
        db.session.commit()

    except Exception:
        db.session.rollback()
        print("Exception", str(Exception))
        return "Sorry, Error, Please try again later", str(Exception)
    return favorite
