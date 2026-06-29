import subprocess
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import set_access_cookies, create_access_token , jwt_required , get_jwt_identity
import hmac
import hashlib
from models import db, User

bcrypt = Bcrypt() 

api_routes = Blueprint('api', __name__)

# Home route defined in app.py

@api_routes.route('/api/test/', methods=['GET'])
def test_route():
  return jsonify({
    "message": "Backend testing w/ Flask, remove me later"
  })

# route for registering new user
@api_routes.route("/register/", methods=["POST"])
def register():

  data = request.json

  username = data.get("username", "").strip()
  password = data.get("password", "")

  if not username or not password:
    return jsonify({"error": "Username and password required"}), 400

  hashed_pw = bcrypt.generate_password_hash(
    data["password"]
  ).decode("utf-8")

  existing_user = User.query.filter_by(username=data["username"]).first()
  if existing_user:
    return jsonify({"error": "Username already taken"}), 400
  
  new_user = User(
    username=data["username"],
    password_hash=hashed_pw
  )
  try:
    db.session.add(new_user)
    db.session.commit()
  except IntegrityError:
    db.session.rollback()
    return jsonify({"error": "Username already taken"}), 400

  return jsonify({"message": "User created"}), 201

@api_routes.route("/login/", methods=["POST"])
def login():
  data = request.json
  
  username = data.get("username", "").strip()
  password = data.get("password", "")

  if not username or not password:
    return jsonify({"error": "Username and password required"}), 400

  user = User.query.filter_by(username=data["username"]).first()

  if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
    return jsonify({"message": "Bad credentials"}), 401
  
  access_token = create_access_token(identity=user.username)

  response = jsonify({"message": "Login successful"})
  set_access_cookies(response, access_token)

  return response

@api_routes.route("/dashboard/")
@jwt_required()
def dashboard():
  username = get_jwt_identity()
  
  user = User.query.filter_by(username=username).first()

  if user:
    return jsonify({"message": f"Welcome {user.username}"})
  else:
    return jsonify({"message": "User not found"}), 404


# github pushes should go directly to the web-app (for convenience)
@api_routes.route('/api/update-server/', methods=['POST'])
def update_server():
  signature = request.headers.get('X-Hub-Signature-256')
  return jsonify({"message": "Securely verified"}), 200
