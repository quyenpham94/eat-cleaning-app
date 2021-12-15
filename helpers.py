def get_ingredients_from_api_response(data):
    results = data['results']
    ingredients = []

    for result in results:
        ingredient = {
            'id': results['id'],
            'title': results['title']
        }
        ingredients.append(ingredient)
    return ingredients