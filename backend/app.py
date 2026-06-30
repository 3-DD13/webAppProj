import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from models import db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIST = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend', 'dist'))

# app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path='/')
app = Flask(__name__)

# database config
load_dotenv(os.path.join(BASE_DIR, '.env'))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'site.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print(f"DEBUG: JWT_SECRET_KEY is {os.environ.get('JWT_SECRET_KEY')}") # Check your terminal

db.init_app(app)

app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY")
app.config['JWT_TOKEN_LOCATION'] = ["cookies"]
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

# shares cookies between localhost and 127
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'

jwt = JWTManager(app)
CORS(app, resources={
  r"/*": 
  {"origins": [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://hjuarez.pythonanywhere.com"
    ]}}, supports_credentials=True)

from routes import api_routes, bcrypt
bcrypt.init_app(app)
app.register_blueprint(api_routes)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
  if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
    return send_from_directory(app.static_folder, path)
  else:
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
  with app.app_context():
    db.create_all()
  app.run(debug=True)