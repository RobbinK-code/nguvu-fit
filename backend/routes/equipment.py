from flask import Blueprint, request, jsonify

from gym_equipment import get_equipment, EQUIPMENT
from decorators import login_required

equipment_bp = Blueprint("equipment", __name__, url_prefix="/equipment")

FREE_TEASER_LIMIT = 1


@equipment_bp.get("")
@login_required
def list_equipment(user):
    muscle_group = request.args.get("muscle_group")
    data = get_equipment(muscle_group) if muscle_group else EQUIPMENT

    is_premium = user.has_active_subscription()

    if is_premium:
        return jsonify({"is_premium": True, "equipment": data}), 200

    if muscle_group:
        limited = data[:FREE_TEASER_LIMIT]
    else:
        limited = {k: v[:FREE_TEASER_LIMIT] for k, v in data.items()}

    return jsonify({"is_premium": False, "equipment": limited}), 200
