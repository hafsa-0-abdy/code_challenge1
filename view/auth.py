from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash,generate_password_hash
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required,blacklist

from models import db, User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route("/login", methods=['POST'])
def login():
    data = request.get_json()

    # Check if required fields are provided
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400

    # Find user by email
    user = User.query.filter_by(email=data['email']).first()

    # Validate email and password
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=user.id)
    return jsonify({"message": "Login successful", "access_token": access_token}), 200

# current user
@auth_bp.route("/current_user", methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"username": user.username, "email": user.email})

# log out user
@auth_bp.route("/logout", methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt_identity()
    blacklist.add(jti)
    return jsonify({"message": "Logged out successfully"}), 200

# update user profile 
@auth_bp.route("/users/<int:user_id>", methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    current_user_id = get_jwt_identity()
    if user.id != current_user_id:
        return jsonify({"error": "Unauthorized to update this user"}), 403

    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)

    db.session.commit()
    return jsonify({"message": "User updated successfully"})

# update user password 
@auth_bp.route("/users/<int:user_id>/password", methods=['PUT'])
@jwt_required()
def update_password(user_id):
    data = request.get_json()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    current_user_id = get_jwt_identity()
    if user.id != current_user_id:
        return jsonify({"error": "Unauthorized to update this user's password"}), 403

    if not check_password_hash(user.password, data['old_password']):
        return jsonify({"error": "Invalid old password"}), 400

    user.password = generate_password_hash(data['new_password'])
    db.session.commit()
    return jsonify({"message": "User password updated successfully"})

# delete user account
@auth_bp.route("/users/<int:user_id>", methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    current_user_id = get_jwt_identity()
    if user.id != current_user_id:
        return jsonify({"error": "Unauthorized to delete this user"}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})