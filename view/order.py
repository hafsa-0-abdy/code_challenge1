from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, User

order_bp = Blueprint("order_bp", __name__)

@order_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    data = request.get_json()
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if 'date' not in data or 'detail' not in data or 'total' not in data:
        return jsonify({"error": "Missing required fields: 'date', 'detail', or 'total'."}), 400

    order = Order(
        date=data['date'],
        detail=data['detail'],
        total=data['total'],
        user_id=user.id
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({"message": "Order created successfully", "order_id": order.id}), 201

                    #UPDATE

@order_bp.route('/orders/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    data = request.json
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    order = Order.query.get(order_id)
    if not order:
        abort(404, "Order not found")

    if user.email != user_email:
        return jsonify({"error": "Unauthorized to update this order"}), 403

    order.date = data.get('date', order.date)
    order.detail = data.get('detail', order.detail)
    order.total = data.get('total', order.total)

    db.session.commit()
    return jsonify({"message": "Order updated successfully"})
                       # DELETE

@order_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    order = Order.query.get(order_id)
    if not order:
        abort(404, "Order not found")

    if user.email != user_email:
        return jsonify({"error": "Unauthorized to delete this order"}), 403

    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted successfully"})
