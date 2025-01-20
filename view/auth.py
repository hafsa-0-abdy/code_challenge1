from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash,generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db, User, TokenBlocklist
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from models import db, User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    
    user = User.query.filter_by(email=email).first()

    if user and user.password == password :
        access_token = create_access_token(identity=user.email)
        return jsonify({"access_token": access_token}), 200

    else:
        return jsonify({"error": "Either email/password is incorrect"}), 404
    
# current user
@auth_bp.route("/current_user", methods=['GET'])
@jwt_required()
def get_current_user():

    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"username": user.username, "email": user.email})

# log out user
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify({"success ":"Logged out successfully"})

# update user profile 
@auth_bp.route("/users", methods=['PUT'])
@jwt_required()
def update_user():
    user_email = get_jwt_identity()
    data = request.get_json()
    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    current_user_id = get_jwt_identity()
    if user.id != current_user_id:
        return jsonify({"error": "Unauthorized to update this user"}), 403

    user.username = data.get('username', user.username)
    user.password = data.get('password', user.password)

    db.session.commit()
    return jsonify({"message": "User updated successfully"})

# update user password 
@auth_bp.route("/users/password", methods=['PUT'])
@jwt_required()
def update_password(user_id):
    data = request.get_json()
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.email != user_email:
        return jsonify({"error": "Unauthorized to update this user's password"}), 403

    if not check_password_hash(user.password, data['old_password']):
        return jsonify({"error": "Invalid old password"}), 400

    user.password = generate_password_hash(data['new_password'])
    db.session.commit()
    return jsonify({"message": "User password updated successfully"})

# delete user account
@auth_bp.route("/users/deleteaccount", methods=['DELETE'])
@jwt_required()
def delete_user():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.email != user_email:
        return jsonify({"error": "Unauthorized to delete this user"}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})