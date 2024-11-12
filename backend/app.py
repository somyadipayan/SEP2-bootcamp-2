from flask import Flask, jsonify, request, send_file
from config import Config
from models import *
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from werkzeug.utils import secure_filename
import os 

app = Flask(__name__)
app.config.from_object(Config)

#Initializing objects in app context
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)


def createAdmin():
    existing_admin = User.query.filter_by(role='admin').first()
    if existing_admin:
        return jsonify({"message":"Admin is already there"}), 200
    try:
        admin = User(username="admin", email="admin@store.com", role="admin", password="1")
        db.session.add(admin)
        db.session.commit()
        return jsonify({"message":"Admin Created Successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500

with app.app_context():
    db.create_all()
    createAdmin()

CORS(app, supports_credentials=True)


@app.route("/")
def test():
    return "Hello World"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    role = data.get("role")
    password = data.get("password")

    if not username or not email or not role or not password:
        return jsonify({"error":"Required Fields are Missing"}), 400
    
    existing_user= User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first()

    if existing_user:
        return  jsonify({"error":"User already Exists"}), 400
    
    try:
        user = User(
            username=username,
            email=email,
            role=role,
            password=password
                    )
        
        db.session.add(user)
        db.session.commit()
        return jsonify({"message":"Registration Successful"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500

# Login API
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error":"Required Fields are Missing"}), 400

    user = User.query.filter_by(email=email).first()

    # if user is not found or password doesn't match
    if not user or not bcrypt.check_password_hash(user.password,password):
        return jsonify({"error":"Invalid Credentials"}), 401

    access_token = create_access_token(identity={
        "email":user.email,
        "role": user.role,
        "id": user.id
    })

    user.lastLoggedIn = datetime.now()
    db.session.commit()
    return jsonify({"message":"login successful","access_token":access_token}), 201


# @app.route("/protected", methods=["GET"])
# @jwt_required()
# def protected():
#     return "Hey you can access this!!"

# @app.route("/protected/admin", methods=["GET"])
# @jwt_required()
# def admin_protected():
#     current_user = get_jwt_identity()
#     print(current_user)
#     if current_user['role'] != 'admin':
#         return "UNAUTHORIZED"
#     return "Hey you can access this!!"

@app.route("/get-user-info",methods=["GET"])
@jwt_required()
def get_user_info():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id = current_user['id']).first()
    user_data = {
        "username" : user.username,
        "email" : user.email,
        "role" : user.role,
        "id" : user.id
    }
    return jsonify({"user":user_data}), 201


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message":"Logged out successfully"})
    unset_jwt_cookies(response)
    return response, 200

#CRUD ON CATEGORIES
#CREATE
@app.route("/category", methods=["POST"])
@jwt_required()
def create_category():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error":"UNAUTHORIZED"}), 401

    name = request.form.get("name")
    description = request.form.get("description")
    advertisement = request.files.get("advertisement") # PDF FILE
    
    if not name or not description or not advertisement:
        return jsonify({"error":"Required Fields are Missing"}), 400
    
    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return jsonify({"error":"Category Already Exists"}), 400
    
    advertisement_filename = secure_filename(name + ".pdf")
    advertisement_document_path = os.path.join(app.config["UPLOAD_FOLDER"], advertisement_filename)
    os.makedirs(os.path.dirname(advertisement_document_path), exist_ok=True)
    advertisement.save(advertisement_document_path)
    print(advertisement_document_path)
    try:
        category = Category(name=name, description=description, category_advertisement_document_path=advertisement_filename)
        db.session.add(category)
        db.session.commit()
        return jsonify({"message":"Category Created Successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500

# READ ALL CATEGORIES
@app.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    categories_data = []
    for category in categories:
        categories_data.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "category_advertisement_document_path": category.category_advertisement_document_path,
            "products": [product.name for product in category.products]
        })
    return jsonify({"categories":categories_data}), 200
    

# READ A SINGLE CATEGORY BY ID
@app.route("/category/<int:id>", methods=["GET"])
def get_category(id):
    category = Category.query.filter_by(id=id).first()
    if not category:
        return jsonify({"error":"Category not found"}), 404
    category_data = {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "category_advertisement_document_path": category.category_advertisement_document_path,
        "products": [product.name for product in category.products]
    }
    return jsonify(category_data), 200

# SERVE PDF IN BACKEND
@app.route("/category/<int:id>/advertisement", methods=["GET"])
def view_advertisement(id):
    category = Category.query.filter_by(id=id).first()
    if not category:
        return jsonify({"error":"Category not found"}), 404
    advertisement = category.category_advertisement_document_path
    advertisement_path = os.path.join(app.config["UPLOAD_FOLDER"], advertisement)
    return send_file(advertisement_path, mimetype="application/pdf")
   
# UPDATE A CATEGORY BY ID
@app.route("/category/<int:id>", methods=["PUT"])
@jwt_required()
def update_category(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error":"UNAUTHORIZED"}), 401

    category = Category.query.filter_by(id=id).first()
    if not category:
        return jsonify({"error":"Category not found"}), 404
    name = request.form.get("name")
    description = request.form.get("description")
    advertisement = request.files.get("advertisement") # PDF FILE

    if advertisement:
        advertisement_filename = secure_filename(name + ".pdf")
        advertisement_document_path = os.path.join(app.config["UPLOAD_FOLDER"], advertisement_filename)
        os.makedirs(os.path.dirname(advertisement_document_path), exist_ok=True)
        advertisement.save(advertisement_document_path)
        category.category_advertisement_document_path = advertisement_filename
    
    if not(name==""):
        category.name = name

    if not(description==""):
        category.description = description
    
    try:
        db.session.commit()
        return jsonify({"message":"Category Updated Successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500
    
# DELETE A CATEGORY BY ID
@app.route("/category/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_category(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error":"UNAUTHORIZED"}), 401

    category = Category.query.filter_by(id=id).first()
    if not category:
        return jsonify({"error":"Category not found"}), 404
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message":"Category Deleted Successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500
    
# CRUD ON PRODUCTS
# CREATE A PRODUCT # Can be only done by admin and Managers
@app.route("/product", methods=["POST"])
@jwt_required()
def create_product():
    current_user = get_jwt_identity()
    # if current user is a user
    if current_user['role'] == 'user':
        return jsonify({"error":"UNAUTHORIZED"}), 401
    data = request.json
    # name, price, unit, quantity, category_id, creator_id
    category_id = data.get("category_id")
    name = data.get("name")
    price = data.get("price")
    unit = data.get("unit")
    quantity = data.get("quantity")
    creator_id = current_user['id']

    if not category_id or not name or not price or not unit or not quantity or not creator_id:
        return jsonify({"error":"Required Fields are Missing"}), 400
    
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return jsonify({"error":"Category not found"}), 404
    
    product = Product.query.filter_by(name=name).first()
    if product:
        return jsonify({"error":"Product already exists"}), 409
    
    if price <= 0:
        return jsonify({"error":"Price must be greater than 0"}), 400

    if quantity <= 0:
        return jsonify({"error":"Quantity must be greater than 0"}), 400

    try:
        product = Product(name=name, price=price, unit=unit, quantity=quantity, category_id=category_id, creator_id=creator_id)
        db.session.add(product)
        db.session.commit()
        return jsonify({"message":"Product Created Successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500

# GET ALL PRODUCTS
@app.route("/product", methods=["GET"])
def get_products():
    categories = Category.query.all()
    data = []
    for category in categories:
        # Populating products for a single category
        products = []
        for product in category.products:
            products.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "unit": product.unit,
                "quantity": product.quantity,
                "creator_id": product.creator_id,
                "creator": product.creator.username
            })
        data.append({
            "id":category.id,
            "name":category.name,
            "pdf":category.category_advertisement_document_path,
            "products": products
        })
    return jsonify(data), 200

# get a single product
@app.route("/product/<int:id>", methods=["GET"])
def get_product(id):
    product = Product.query.filter_by(id=id).first()
    if not product:
        return jsonify({"error":"Product not found"}), 404
    product_data = {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "unit": product.unit,
                "quantity": product.quantity,
                "creator_id": product.creator_id,
                "creator": product.creator.username,
                "category_id": product.category_id,
                "category": product.category.name
                }
    
    return jsonify(product_data), 200

# UPDATE A PRODUCT # Can be only done by admin and Managers
@app.route("/product/<int:id>", methods=["PUT"])
@jwt_required()
def update_product():
    current_user = get_jwt_identity()
    # if current user is a user
    if current_user['role'] == 'user':
        return jsonify({"error":"UNAUTHORIZED"}), 401
    
    product = Product.query.filter_by(id=id).first()

    if not product:
        return jsonify({"error":"Product not found"}), 404

    data = request.json

    name = data.get("name")
    price = data.get("price")
    unit = data.get("unit")
    quantity = data.get("quantity")

    if not name or not price or not unit or not quantity:
        return jsonify({"error":"Required Fields are Missing"}), 400
    
    if price <= 0:
        return jsonify({"error":"Price must be greater than 0"}), 400

    if quantity <= 0:
        return jsonify({"error":"Quantity must be greater than 0"}), 400
    
    product.name = name
    product.quantity = quantity
    product.price = price
    product.unit - unit

    try: 
        db.session.commit()
        return jsonify({"message":f"Product {product.name} updated Successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500
    
# DELETE A PRODUCT

@app.route("/product/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_product():
    current_user = get_jwt_identity()
    # if current user is a user
    if current_user['role'] == 'user':
        return jsonify({"error":"UNAUTHORIZED"}), 401
        
    product = Product.query.filter_by(id=id).first()

    if not product:
        return jsonify({"error":"Product not found"}), 404    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message":f"Product deleted Successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500

# CART
# Add to Cart
@app.route("/add-to-cart", methods=['POST'])
@jwt_required()
def add_to_cart():
    current_user = get_jwt_identity()
    if current_user['role'] != 'user':
        return jsonify({"error":"You're not supposed to do this"}), 401
    data = request.json

    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity:
        return jsonify({"error":"Required Fields are Missing"}), 400
    
    product = Product.query.filter_by(id=product_id).first()

    if not product:
        return jsonify({"error":"Product not found"}), 404  

    if quantity <= 0:
        return jsonify({"error":"Quantity must be greater than 0"}), 400
    
    if product.quantity <= quantity:
        return jsonify({"error":"Not enough products in stock"}), 400  

    user_cart = ShoppingCart.query.filter_by(user_id=current_user["id"]).first()

    if not user_cart:
        user_cart = ShoppingCart(user_id=current_user["id"])
        try: 
            db.session.add(user_cart)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error":str(e)}), 500 

    cart_item = CartItems.query.filter_by(shopping_cart_id=user_cart.id,product_id=product_id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItems(shopping_cart_id=user_cart.id,
                            product_id=product_id,
                            quantity=quantity)
        db.session.add(cart_item)

    try: 
        db.session.commit()
        return jsonify({"message":f"{product.name} added to cart Successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500 

# VIEW CART

# UPDATE THE CART ITEM (PUT)

# REMOVE THE CART ITEM (DELETE)

# CLEAR THE CART (DELETE)

# ORDER
@app.route("/place-order", methods=["POST"])
@jwt_required()
def place_order():
    current_user = get_jwt_identity()
    if current_user['role'] != 'user':
        return jsonify({"error":"You're not supposed to do this"}), 401
    user_cart = ShoppingCart.query.filter_by(user_id=current_user["id"]).first()
    if not user_cart:
        return jsonify({"message":"Your Cart is empty!"}), 201
    order_items = []
    total_amount = 0
    for item in user_cart.cart_items:
        # QUANTITY CUSTOMER WANTS TO BUY >= QUANTITY IN STOCK
        if item.quantity >= item.product.quantity:
            return jsonify({"error":"Not enough products in stock"}), 400  
        total_amount += item.product.price * item.quantity
        order_item = OrderItems(product_id=item.product_id,
                                 quantity = item.quantity
                                )
        order_items.append(order_item)
        item.product.quantity -= item.quantity
    new_order = Order(user_id = current_user["id"],
                      total_amount = total_amount,
                      order_items = order_items
                      )
    try:
        db.session.add(new_order)
        db.session.delete(user_cart)
        db.session.commit()
        return jsonify({"message":"Order Placed Successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}), 500 




if __name__ == "__main__":
    app.run(debug = True)