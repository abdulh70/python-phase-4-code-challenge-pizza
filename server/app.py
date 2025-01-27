#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
import os
from models import db, Restaurant, RestaurantPizza, Pizza

# setting up the base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# initializing the Flask application
app = Flask(__name__)
# Configuring the database URI and turning off modification tracking
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Ensuring JSON responses aren't compacted
app.json.compact = False

# Initializing the database and migration objects
db.init_app(app)
migrate = Migrate(app, db)

# Setting up the API object
api = Api(app)

# Resource for handling the collection of all restaurants
class Restaurants(Resource):
    def get(self):
        restaurants = [n.to_dict() for n in Restaurant.query.all()]
        for hero in restaurants:
            hero.pop('restaurant_pizzas', None)
        return make_response(restaurants, 200)

# Adding the restaurants resource to the API at the restaurants endpoint
api.add_resource(Restaurants, "/restaurants")


class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404
        response_dict = restaurant.to_dict()
        return response_dict, 200
    
    def delete(self, id):
        # Query for a restaurant by ID
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant is None:
            # Return a 404 error if the restaurant isn't found
            return {"error": "Restaurant not found"}, 404
        # Delete the restaurant from the database
        db.session.delete(restaurant)
        db.session.commit()
        # Return an empty response with a 204 status code
        return {}, 204

api.add_resource(RestaurantByID, "/restaurants/<int:id>")

# Resource for handling the collection of all pizzas
class Pizzas(Resource):
    def get(self):
        # Query all pizzas and convert them to dictionaries
        response_dict_list = [n.to_dict() for n in Pizza.query.all()]
        # Return the list of pizzas with a 200 status code
        response = make_response(
            response_dict_list,
            200,
        )
        return response

# adding the Pizzas resource to the API at the pizzas endpoint
api.add_resource(Pizzas, "/pizzas")

class RestaurantPizzas(Resource):
    def post(self):
        try:
            # get the JSON data from the request
            data = request.get_json()
            price = int(data.get('price'))
            # create a new RestaurantPizza object
            restaurant_pizza = RestaurantPizza(
                pizza_id=data.get('pizza_id'),
                restaurant_id=data.get('restaurant_id'),
                price=price,
            )
            #  commit the new RestaurantPizza to the database
            db.session.add(restaurant_pizza)
            db.session.commit()
            # Conver the RestaurantPizza to a dictionary and return it with a 201 status code
            response_dict = restaurant_pizza.to_dict()
            return make_response(response_dict, 201)
        except ValueError as e:
            return {"errors": ["Price must be between 1 and 30"]}, 400
        except Exception as e:
            return {"errors": ["validation errors"]}, 400

# ading the RestaurantPizzas resource to the API at the endpoint
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)