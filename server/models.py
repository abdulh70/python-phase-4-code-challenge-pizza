from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

# Setting up metadata with a naming convention for foreign keys
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

# Definition of  the Restaurant model
class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"  # This is the table name in our database


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Setting up a relationship with RestaurantPizza
    pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade="all, delete-orphan")

    # This rule helps avoid circular references during serialization
    serialize_rules = ('-pizzas.restaurant',)

    # This gives us a nice string representation for debugging
    def __repr__(self):
        return f"<Restaurant {self.name}>"

    # Method to convert a Restaurant instance to a dictionary
    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'restaurant_pizzas': [restaurant_pizza.to_dict(include_restaurant=False) for restaurant_pizza in self.pizzas]
        }
        return data

# Define the Pizza model
class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"  # This is the table name in our database

    # These are the columns in the pizzas table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Setting up a relationship with RestaurantPizza
    restaurants = db.relationship('RestaurantPizza', back_populates='pizza', cascade="all, delete-orphan")

    # This rule helps avoid circular references during serialization
    serialize_rules = ('-restaurants.pizza',)

    # This gives us a nice string representation for debugging
    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

    # Method to convert a Pizza instance to a dictionary
    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }
        return data

# Define the RestaurantPizza model
class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"  # This is the table name in our database

    # These are the columns in the restaurant_pizzas table
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))

    # Setting up relationships with Restaurant and Pizza
    restaurant = db.relationship('Restaurant', back_populates='pizzas')
    pizza = db.relationship('Pizza', back_populates='restaurants')

    serialize_rules = ('-restaurant.pizzas', '-pizza.restaurants')

   
    @validates('price')
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")
        return price


    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"

    # Method to convert a RestaurantPizza instance to a dictionary
    def to_dict(self, include_restaurant=True):
        data = {
            'id': self.id,
            'price': self.price,
            'pizza_id': self.pizza_id,
            'restaurant_id': self.restaurant_id,
            'pizza': self.pizza.to_dict()
        }
        if include_restaurant:
            data['restaurant'] = {'id': self.restaurant.id, 'name': self.restaurant.name}
        return data