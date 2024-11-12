from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    lastLoggedIn = db.Column(db.DateTime, default=datetime.now)
    
    def __init__(self, username, email, role, password):
        self.username = username
        self.email = email
        self.role = role
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    category_advertisement_document_path = db.Column(db.String(200)) # Storing the file path instead of the actual file
    products = db.relationship('Product', back_populates='category', cascade='all, delete-orphan')
    def __init__(self, name, description, category_advertisement_document_path):
        print(category_advertisement_document_path)
        self.name = name
        self.description = description
        self.category_advertisement_document_path = category_advertisement_document_path



class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.relationship('Category', back_populates='products') # Many-One 
    creator = db.relationship('User', backref='products') # Many-one
    cart_items = db.relationship('CartItems', back_populates='product', cascade='all, delete-orphan') 
    def __init__(self, name, price, unit, quantity, category_id, creator_id):
        self.name = name
        self.price = price
        self.unit = unit
        self.quantity = quantity
        self.category_id = category_id
        self.creator_id = creator_id

class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='shopping_cart')
    cart_items = db.relationship('CartItems', back_populates="shopping_cart", cascade="all, delete-orphan")

    def __init__(self, user_id):
        self.user_id = user_id

class CartItems(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', back_populates='cart_items')
    quantity = db.Column(db.Integer, nullable=False)
    shopping_cart_id = db.Column(db.Integer, db.ForeignKey('shopping_cart.id'), nullable=False)
    shopping_cart = db.relationship('ShoppingCart', back_populates='cart_items')

    def __init__(self, product_id, quantity, shopping_cart_id):
        self.product_id = product_id
        self.quantity = quantity
        self.shopping_cart_id = shopping_cart_id

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='orders')
    order_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

class OrderItems(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref='order_items')
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    order = db.relationship('Order', backref='order_items')