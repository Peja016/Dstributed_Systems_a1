from flask import Flask, jsonify, request

from functools import wraps
from models import User

app = Flask(__name__)

def user_required(f):
    @wraps(f)
    def wrapper(id, *args, **kwargs):
        user = User.findById(int(id))
        if not user:
            return jsonify({"error": "User not found"}), 404
        return f(user, *args, **kwargs)
    return wrapper

@app.before_request
def check_json_header():
    if request.method in ["POST", "PUT"]:
        if request.content_type != "application/json":
            return jsonify({
                "error": "Unsupported Media Type",
                "message": "The server only accepts 'Content-Type: application/json'"
            }), 415

@app.route('/api/users', methods=['GET'])
def get_users():
# Return list of all users
    users = [user.to_dict() for user in User.getAllUsers()]
    return jsonify(users)

@app.route('/api/users/<id>', methods=['GET'])
@user_required
def get_user(user):
# Return specific user
    return jsonify(user.to_dict())

@app.route('/api/users', methods=['POST'])
def create_user():
# Create new user from request data
    data = request.get_json()
    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "Invalid data"}), 400
    new_user = User(data["name"], data["email"])
    return jsonify(new_user.to_dict()), 201

@app.route('/api/users/<id>', methods=['PUT'])
@user_required
def update_user(user):
# Update existing user
    data = request.get_json()
    if not data:
         return jsonify({"error": "No update data provided"}), 400
    user.update_user(name=data.get("name"), email=data.get("email"))
    return jsonify({"message": "The user data has updated"})

@app.route('/api/users/<id>', methods=['DELETE'])
@user_required
def delete_user(user):
    user.delete()
    return jsonify({"message": "The user is deleted"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
