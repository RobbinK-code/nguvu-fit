from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request

from config import db
from models import User, WorkoutLog, Payment
from schemas import user_schema
from decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/users")
@admin_required
def list_users(admin_user):
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([user_schema.dump(u) for u in users]), 200


@admin_bp.patch("/users/<int:id>/toggle-admin")
@admin_required
def toggle_admin(admin_user, id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    user.is_admin = not user.is_admin
    db.session.commit()
    return jsonify(user_schema.dump(user)), 200


@admin_bp.patch("/users/<int:id>/subscription")
@admin_required
def set_subscription(admin_user, id):
    """Manually grant or revoke a subscription - for comps, refunds, or
    payments taken outside the app (e.g. cash, a manual M-Pesa transfer)."""
    user = db.session.get(User, id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    json_data = request.get_json(silent=True) or {}
    action = json_data.get("action")

    if action == "grant":
        days = json_data.get("days", 30)
        user.subscription_status = "active"
        user.subscription_expires_at = datetime.utcnow() + timedelta(days=int(days))
    elif action == "revoke":
        user.subscription_status = "expired"
        user.subscription_expires_at = None
    else:
        return jsonify({"error": "action must be 'grant' or 'revoke'."}), 400

    db.session.commit()
    return jsonify(user_schema.dump(user)), 200


@admin_bp.delete("/users/<int:id>")
@admin_required
def delete_user(admin_user, id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    if user.id == admin_user.id:
        return jsonify({"error": "You can't delete your own account."}), 400
    db.session.delete(user)
    db.session.commit()
    return "", 204


@admin_bp.get("/stats")
@admin_required
def stats(admin_user):
    return jsonify(
        {
            "total_users": User.query.count(),
            "active_subscriptions": User.query.filter_by(subscription_status="active").count(),
            "total_workouts_logged": WorkoutLog.query.count(),
            "successful_payments": Payment.query.filter_by(status="success").count(),
            "revenue_kes": db.session.query(db.func.coalesce(db.func.sum(Payment.amount), 0))
            .filter(Payment.status == "success")
            .scalar(),
        }
    ), 200
