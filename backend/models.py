from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User db model
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), unique=True, nullable=False)
  password_hash = db.Column(db.String(256), nullable=False)