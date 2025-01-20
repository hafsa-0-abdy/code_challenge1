from flask import Blueprint, jsonify, request, abort
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User

user_bp = Blueprint("user_blueprint", __name__)
@user_bp.route('/users', methods=['POST'])

def create_user():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 409

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully"})
    
    
@user_bp.route('/users', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.json
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user:
        abort(404, "User not found")

    
    if user.email != user_email:
        return jsonify({"error": "Unauthorized to update this user"}), 403

    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)

    db.session.commit()
    return jsonify({"message": "User updated successfully"})

@user_bp.route('/users/delete', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user:
        abort(404, "User not found")

    
    if user.email != user_email:
        return jsonify({"error": "Unauthorized to delete this user"}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})
