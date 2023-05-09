from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from secrets import token_hex
from werkzeug.security import generate_password_hash

# from flask_login import UserMixin

# Instantiate the database
db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),nullable = False,unique=True)
    email = db.Column(db.String(100),nullable = False,unique=True)
    password = db.Column(db.String,nullable=False)
    first_name = db.Column(db.String(50), nullable = False)
    last_name = db.Column(db.String(50))
    date_joined = db.Column(db.DateTime,nullable = False, default=datetime.utcnow())
    apitoken = db.Column(db.String,unique=True)

    cart_items = db.relationship("Carts",foreign_keys='Carts.user_id',back_populates="user")

    def __init__(self, username, email, password, first_name,last_name):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.apitoken = token_hex(16)

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()

    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id':self.id,
            'username':self.username,
            'email':self.email,
            'apitoken':self.apitoken,
        }



class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable = False, unique=True)
    price = db.Column(db.Float, nullable = False)
    description = db.Column(db.String(500), nullable = False)
    image_url = db.Column(db.String)

    associated_carts = db.relationship("Carts",foreign_keys='Carts.product_id',back_populates="product")

    def __init__(self, product_name, price, description, image_url):
        self.product_name = product_name
        self.price = price
        self.description = description
        self.image_url = image_url

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()

    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id":self.id,
            'product_name':self.product_name,
            'price':"${:,.2f}".format(self.price),
            'description':self.description,
            'image_url':self.image_url,
        }
    
class Carts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_quantity = db.Column(db.Integer,nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id),nullable=False)
    user = db.relationship("Users",back_populates="cart_items",foreign_keys=[user_id])
    
    product_id = db.Column(db.Integer, db.ForeignKey(Products.id),nullable=False)
    product = db.relationship("Products",back_populates="associated_carts",foreign_keys=[product_id])
    
    def __init__(self, user_id, product_id, item_quantity):
        self.user_id = user_id
        self.product_id = product_id
        self.item_quantity = item_quantity

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()

    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()

    def makeCartDict(self):
        product = self.product
        cart_dict = {
            "user_id":self.user_id,
            "item_quantity":self.item_quantity

        }
        for key, value in product.to_dict().items():
            if key != "id":
                cart_dict[key] = value
            else:
                cart_dict["item_id"] = value
        
        total_cost = product.price * cart_dict["item_quantity"] 
        cart_dict["total_item_cost_number"] = total_cost
        cart_dict["total_item_cost"] = "${:,.2f}".format(total_cost)
        return cart_dict



    
    
