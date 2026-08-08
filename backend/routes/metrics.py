from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config import db
from models import BodyMetricLog
from schemas import body_metric_log_schema, body_metric_logs_schema
from decorators import subscription_required

metrics_bp = Blueprint("metrics", __name__, url_prefix="/metrics")


@metrics_bp.get("")
@subscription_required
def list_metrics(user):
    logs = (
        BodyMetricLog.query.filter_by(user_id=user.id)
        .order_by(BodyMetricLog.recorded_at.asc())
        .all()
    )
    return jsonify(body_metric_logs_schema.dump(logs)), 200


@metrics_bp.post("")
@subscription_required
def create_metric(user):
    json_data = request.get_json(silent=True) or {}
    try:
        data = body_metric_log_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    log = BodyMetricLog(user_id=user.id, **data)
    db.session.add(log)

    # Keep the profile's headline weight_kg (used for BMI/pace) in sync
    # with the latest logged entry, so people don't have to update it
    # in two places.
    if data.get("weight_kg"):
        user.weight_kg = data["weight_kg"]

    db.session.commit()
    return jsonify(body_metric_log_schema.dump(log)), 201


@metrics_bp.delete("/<int:id>")
@subscription_required
def delete_metric(user, id):
    log = BodyMetricLog.query.filter_by(id=id, user_id=user.id).first()
    if not log:
        return jsonify({"error": "Entry not found."}), 404
    db.session.delete(log)
    db.session.commit()
    return "", 204
