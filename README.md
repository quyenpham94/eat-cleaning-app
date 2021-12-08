# eat-cleaning-app

This project take the information from the Spoonacular API (https://spoonacular.com/)

Project Proposal

Goal:
The website will be designed to achieve a healthy diet for everyone. It is inspired by the idea of clean eating. Clean eating is traditionally defined as eating simple, whole foods without  any artificial ingredients (eliminate processed foods, trans fats, heavy saturated fats, added sugar, and refined grains). Thus, the website will help users calculate the calories, trans fats and added sugar so that they can control the nutrition they eat every meal.
The demographic of users:
Everyone who wants to have a healthy life or diet process can use this website to support their goal. It could be easy-to-use so that the user does not need to know some specific high technology. The user just needs to search/click on the food they ate on their meal and the app will calculate the nutrition itself and return to the user.

Data Sources:
Spoonacular API. you just need to create an account to get a free access to their dataset
Project details:

Database schema
The data is built using an endpoint to access a particular dataset of spoonacular API. Using API key to get the data. 
The app uses 4 models: Users, Foods, Recommended Meals, Favorite Meal. The Users model saves the user_id, username, hashed password, and an email to the database. The Foods model saves a foreign key to the user_id, foodname, meal_nutrition to the database. The Recommended Meals model saves a foreign key to the user_id,  foods, meal_nutrition. The Favorite Meal model saves a foreign key to the user_id, foods, meal_nutrition to the database. 
User signup, login, and logout functionality was implemented, as well as authentication and authorization. An account is required to access any of the detailed pages and search functions. Username and email must both be unique

Issue about API
The limit of free data. Each user only has 150 points to access their database using the endpoint. And the dataset might run into the problem of limited available ingredients. Thus, not all of the ingredients the user eats in one meal will be there.

Functionality
Users can create an account and log in when they want to use the app. The data will be stored so the user can check their diet process.
Users can create an empty meal and search/click on foods that they eat in their meal, then add to that empty meal. The app will sum the nutrition of all foods they eat in one meal and return the result. They also can remove and edit if they put wrong items.
They can save their favorite meal in order to use it again in the future.
They also can remove their favorite meal and add another favorite meal (I’m sure their taste will change a lot)
There will be some recommended meals so that the user can choose and follow it to make their meal. 

Technologies:
Python/Flask, PostgreSQL, SQLAlchemy, Heroku, Jinja, RESTful APIs, JavaScript, HTML, CSS

