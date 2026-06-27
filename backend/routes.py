import subprocess
from flask import Blueprint, jsonify

api_routes = Blueprint('api', __name__)
# Home route defined in app.py


@api_routes.route('/api/test/', methods=['GET'])
def test_route():
  return jsonify({
    "message": "Backend testing w/ Flask, remove me later"
  })

# github pushes should go directly to the web-app (more for convenience)
@api_routes.route('/api/update-server/', methods=['POST'])
def update_server():
  try:
    commands = (
      "cd /home/hjuarez/webAppProj && "
      "git fetch --all && "
      "git reset --hard origin/main"
    )
    subprocess.check_call(commands, shell=True)
    return jsonify({"message": "gitHub push recieved"}), 200

  except subprocess.CalledProcessError as e:
    return jsonify({"error": str(e)}), 500
