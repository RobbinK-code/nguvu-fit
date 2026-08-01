from flask import Blueprint, request, jsonify

from models import Exercise
from decorators import login_required
from recommend import generate_plan

plan_bp = Blueprint("plan", __name__, url_prefix="/plan")


@plan_bp.get("")
@login_required
def get_plan(user):
    if not user.height_cm or not user.weight_kg:
        return jsonify(
            {"error": "Set your height and weight in your profile first to generate a plan."}
        ), 400

    days = request.args.get("days", default=3, type=int)
    days = max(1, min(days, 6))

    all_exercises = Exercise.query.all()
    if not all_exercises:
        return jsonify({"error": "No exercises available yet."}), 400

    plan = generate_plan(user, all_exercises, days=days)
    return jsonify(plan), 200
