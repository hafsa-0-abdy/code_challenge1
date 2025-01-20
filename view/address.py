from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Address, User

address_bp = Blueprint("address_bp", __name__)

@address_bp.route('/addresses', methods=['POST'])
@jwt_required()
def create_address():
    data = request.json
    if 'name' not in data or 'street_address' not in data or 'city' not in data or 'postal_code' not in data:
        return jsonify({"error": "Missing required fields: 'name', 'street_address', 'city', or 'postal_code'."}), 400

    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    address = Address(
        name=data['name'],
        street_address=data['street_address'],
        city=data['city'],
        postal_code=data['postal_code'],
        user_id=user.id
    )
    db.session.add(address)
    db.session.commit()

    return jsonify({"message": "Address created successfully", "address_id": address.id}), 201

@address_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    data = request.json
    address = Address.query.get(address_id)

    if not address:
        abort(404, "Address not found")

    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    # if address.user_id != user_id:
    #     return jsonify({"error": "Unauthorized to update this address"}), 403

    address.name = data.get('name', address.name)
    address.street_address = data.get('street_address', address.street_address)
    address.city = data.get('city', address.city)
    address.postal_code = data.get('postal_code', address.postal_code)
    address.user_id = user.id

    db.session.commit()
    return jsonify({"message": "Address updated successfully"})

@address_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    address = Address.query.get(address_id)

    if not address:
        abort(404, "Address not found")

    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if user_email != user.email:
        return jsonify({"error": "Unauthorized to delete this address"}), 403

    db.session.delete(address)
    db.session.commit()
    return jsonify({"message": "Address deleted successfully"})
