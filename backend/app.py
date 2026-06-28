import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')

# database config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'site.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User db model
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), unique=True, nullable=False)
  password_hash = db.Column(db.String(256), nullable=False)

app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY")
app.config['JWT_TOKEN_LOCATION'] = ["cookies"]
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = True

jwt = JWTManager(app)
CORS(app)

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