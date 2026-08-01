from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config import db
from schemas import profile_update_schema, user_schema
from decorators import login_required

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.get("")
@login_required
def get_profile(user):
    return jsonify(user_schema.dump(user)), 200


@profile_bp.patch("")
@login_required
def update_profile(user):
    json_data = request.get_json(silent=True) or {}
    try:
        data = profile_update_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        for field, value in data.items():
            setattr(user, field, value)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({"errors": [str(err)]}), 400

    return jsonify(user_schema.dump(user)), 200
