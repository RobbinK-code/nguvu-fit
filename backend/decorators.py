from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from config import db
from models import User


def current_user():
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    return db.session.get(User, int(user_id))


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = current_user()
        if not user:
            return jsonify({"error": "User not found."}), 404
        return fn(user, *args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = current_user()
        if not user:
            return jsonify({"error": "User not found."}), 404
        if not user.is_admin:
            return jsonify({"error": "Admin access required."}), 403
        return fn(user, *args, **kwargs)

    return wrapper


def subscription_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = current_user()
        if not user:
            return jsonify({"error": "User not found."}), 404
        if not user.has_active_subscription():
            return jsonify({"error": "This feature requires an active subscription."}), 402
        return fn(user, *args, **kwargs)

    return wrapper
