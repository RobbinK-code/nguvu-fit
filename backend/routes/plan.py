from flask import Blueprint, request, jsonify
from uuid import uuid4

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

    FREE_MAX_DAYS = 3

    days = request.args.get("days", default=3, type=int)
    days = max(1, min(days, 6))
    if days > FREE_MAX_DAYS and not user.has_active_subscription():
        return jsonify(
            {
                "error": (
                    f"Plans longer than {FREE_MAX_DAYS} days a week are a premium feature. "
                    "Subscribe to train more days a week."
                )
            }
        ), 402

    all_exercises = Exercise.query.all()
    if not all_exercises:
        return jsonify({"error": "No exercises available yet."}), 400

    refresh = request.args.get("refresh") in ("1", "true", "yes")
    seed = None
    if refresh:
        if not user.has_active_subscription():
            return jsonify(
                {"error": "Regenerating your plan is a premium feature. Subscribe to shuffle any time."}
            ), 402
        seed = str(uuid4())

    plan = generate_plan(user, all_exercises, days=days, seed=seed)
    return jsonify(plan), 200
