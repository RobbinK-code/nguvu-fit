from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config import db
from models import WorkoutLog
from schemas import log_workout_schema, workout_logs_schema
from decorators import login_required

logs_bp = Blueprint("logs", __name__, url_prefix="/logs")


@logs_bp.get("")
@login_required
def get_logs(user):
    logs = (
        WorkoutLog.query.filter_by(user_id=user.id)
        .order_by(WorkoutLog.completed_at.desc())
        .all()
    )
    return jsonify(workout_logs_schema.dump(logs)), 200


@logs_bp.post("")
@login_required
def create_log(user):
    json_data = request.get_json(silent=True) or {}
    try:
        data = log_workout_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    log = WorkoutLog(
        user_id=user.id,
        workout_id=data.get("workout_id"),
        workout_name_snapshot=data["workout_name"],
        duration_minutes=data.get("duration_minutes"),
        notes=data.get("notes"),
    )
    db.session.add(log)
    db.session.commit()
    return jsonify(workout_logs_schema.dump([log])[0]), 201


@logs_bp.get("/stats")
@login_required
def get_stats(user):
    logs = WorkoutLog.query.filter_by(user_id=user.id).all()
    total_minutes = sum(l.duration_minutes or 0 for l in logs)
    return jsonify(
        {
            "total_workouts": len(logs),
            "total_minutes": total_minutes,
        }
    ), 200
