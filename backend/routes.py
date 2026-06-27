from flask import Blueprint, jsonify

api_routes = Blueprint('api', __name__)

@api_routes.route('api/test', methods=['GET'])
def test_route():
  return jsonify({
    "message": "Backend testing w/ Flask, remove me later"
  })