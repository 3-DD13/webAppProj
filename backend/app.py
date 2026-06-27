import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.routes import api_routes

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app)

app.register_blueprint(api_routes)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
  if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
    return send_from_directory(app.static_folder, path)
  else:
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
  app.run(debug=True)