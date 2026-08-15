from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config import db
from schemas import (
    profile_update_schema,
    user_schema,
    workout_logs_schema,
    body_metric_logs_schema,
    payment_export_schema,
)
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


@profile_bp.get("/export")
@login_required
def export_profile(user):
    """Everything the platform holds about this user, in one downloadable
    JSON file - a basic data-portability/right-to-access mechanism."""
    return jsonify(
        {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "profile": user_schema.dump(user),
            "workout_logs": workout_logs_schema.dump(user.workout_logs),
            "body_metric_logs": body_metric_logs_schema.dump(user.body_metric_logs),
            "payments": payment_export_schema.dump(user.payments),
        }
    ), 200


@profile_bp.delete("")
@login_required
def delete_account(user):
    """Self-service account deletion. Requires the current password as
    confirmation so a hijacked/left-open session can't be used to destroy
    the account without re-proving identity."""
    json_data = request.get_json(silent=True) or {}
    password = json_data.get("password")

    if not password or not user.check_password(password):
        return jsonify({"error": "Incorrect password."}), 401

    db.session.delete(user)
    db.session.commit()
    return "", 204
