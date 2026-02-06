"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datastructures import FamilyStructure
from utils import APIException, generate_sitemap

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

jackson_family = FamilyStructure("Jackson", [
    {"id": 1, "first_name": "John", "age": 33, "lucky_numbers": [7, 13, 22]},
    {"id": 2, "first_name": "Jane", "age": 35, "lucky_numbers": [10, 14, 3]},
    {"id": 3, "first_name": "Jimmy", "age": 5, "lucky_numbers": [1]}
])

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Route to generate sitemap
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def read_family():
    return jsonify(jackson_family.get_all_members()), 200

@app.route("/member", methods=["POST"])
def create_member():
    try:
        member = request.json

        if not all(key in member for key in ["id", "first_name", "age", "lucky_numbers"]):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate data types
        if not isinstance(member["id"], int):
            return jsonify({"error": "id must be an integer"}), 400
        if not isinstance(member["first_name"], str):
            return jsonify({"error": "first_name must be a string"}), 400
        if not isinstance(member["age"], int):
            return jsonify({"error": "age must be an integer"}), 400
        if not isinstance(member["lucky_numbers"], list):
            return jsonify({"error": "lucky_numbers must be a list"}), 400

        if jackson_family.get_member(member["id"]):
            return jsonify({"error": "Member with the same ID already exists"}), 400

        jackson_family.add_member(member)

        return jsonify(member), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get a specific family member by ID
@app.route("/member/<int:id>", methods=["GET"])
def get_member(id: int):
    person = jackson_family.get_member(id)
    if person:
        return jsonify(person), 200
    return jsonify({"error": "Member not found"}), 404

@app.route("/member/<int:id>", methods=["DELETE"])
def delete_member(id: int):
    if jackson_family.get_member(id):
        jackson_family.delete_member(id)
        return jsonify({"done": True}), 200
    return jsonify({"error": "Member not found"}), 404

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)