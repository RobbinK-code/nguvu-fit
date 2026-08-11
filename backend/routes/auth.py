from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from config import db
from models import User
from schemas import register_schema, login_schema, user_schema, forgot_password_schema, reset_password_schema
from decorators import login_required, current_user
import mailer
import os

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
def register():
    json_data = request.get_json(silent=True) or {}
    try:
        data = register_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    if User.query.filter_by(email=data["email"].strip().lower()).first():
        return jsonify({"errors": {"email": ["An account with this email already exists."]}}), 400

    user = User(email=data["email"], name=data["name"])
    try:
        user.set_password(data["password"])
    except ValueError as err:
        return jsonify({"errors": {"password": [str(err)]}}), 400

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as err:
        db.session.rollback()
        return jsonify({"errors": [str(err.orig)]}), 400

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user_schema.dump(user)}), 201


@auth_bp.post("/login")
def login():
    json_data = request.get_json(silent=True) or {}
    try:
        data = login_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = User.query.filter_by(email=data["email"].strip().lower()).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user_schema.dump(user)}), 200


@auth_bp.get("/me")
@login_required
def me(user):
    return jsonify(user_schema.dump(user)), 200


@auth_bp.post("/forgot-password")
def forgot_password():
    """Always returns the same generic response regardless of whether the
    email exists, to avoid leaking which addresses have accounts."""
    json_data = request.get_json(silent=True) or {}
    try:
        data = forgot_password_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    generic_response = {
        "message": "If an account exists for that email, we've sent a reset link."
    }

    user = User.query.filter_by(email=data["email"].strip().lower()).first()
    if not user:
        return jsonify(generic_response), 200

    token = user.generate_reset_token()
    db.session.commit()

    frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
    reset_url = f"{frontend_origin}/reset-password?token={token}"

    try:
        mailer.send_password_reset_email(user.email, reset_url)
    except mailer.EmailConfigError as err:
        # Don't leak configuration state to the caller - log it server-side
        # so the site owner sees it in Render's logs, but the public
        # response stays identical either way.
        print(f"[forgot-password] Could not send email: {err}")
    except Exception as err:
        print(f"[forgot-password] Email send failed: {err}")

    return jsonify(generic_response), 200


@auth_bp.post("/reset-password")
def reset_password():
    json_data = request.get_json(silent=True) or {}
    try:
        data = reset_password_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = User.query.filter_by(reset_token=data["token"]).first()
    if not user or not user.reset_token_is_valid(data["token"]):
        return jsonify({"error": "This reset link is invalid or has expired."}), 400

    try:
        user.set_password(data["new_password"])
    except ValueError as err:
        return jsonify({"errors": {"new_password": [str(err)]}}), 400

    user.clear_reset_token()
    db.session.commit()

    return jsonify({"message": "Password updated. You can now log in."}), 200