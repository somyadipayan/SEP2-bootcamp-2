from flask import Flask, jsonify, request
from config import Config
from models import *
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies

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

if __name__ == "__main__":
    app.run(debug = True)