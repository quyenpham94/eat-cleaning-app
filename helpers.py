def add_ingredients_from_api_response(data):
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