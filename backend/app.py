from flask import Flask, jsonify, request
from config import Config
from models import *
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

#Initializing objects in app context
db.init_app(app)
bcrypt.init_app(app)

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

if __name__ == "__main__":
    app.run(debug = True)