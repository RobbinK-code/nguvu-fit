from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from config import db
from models import User
from schemas import register_schema, login_schema, user_schema
from decorators import login_required, current_user

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
