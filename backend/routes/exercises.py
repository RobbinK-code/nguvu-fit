from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from config import db
from models import Exercise
from schemas import exercise_schema, exercises_schema
from decorators import admin_required

exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")


@exercises_bp.get("")
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify(exercises_schema.dump(exercises)), 200


@exercises_bp.post("")
@admin_required
def create_exercise(admin_user):
    json_data = request.get_json(silent=True) or {}
    try:
        data = exercise_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    exercise = Exercise(**data)
    db.session.add(exercise)
    try:
        db.session.commit()
    except (IntegrityError, ValueError) as err:
        db.session.rollback()
        return jsonify({"errors": [str(getattr(err, "orig", err))]}), 400

    return jsonify(exercise_schema.dump(exercise)), 201


@exercises_bp.delete("/<int:id>")
@admin_required
def delete_exercise(admin_user, id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return jsonify({"error": "Exercise not found."}), 404
    db.session.delete(exercise)
    db.session.commit()
    return "", 204
