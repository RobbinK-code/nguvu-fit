from datetime import datetime, timedelta

from flask import Blueprint, jsonify

from config import db
from models import UserChallenge, WorkoutLog
from challenges import CHALLENGES, get_challenge
from decorators import login_required

challenges_bp = Blueprint("challenges", __name__, url_prefix="/challenges")


def _progress_for(enrollment):
    template = get_challenge(enrollment.challenge_id)
    if not template:
        return None

    now = datetime.utcnow()
    end_at = enrollment.started_at + timedelta(days=template["duration_days"])
    days_elapsed = max(0, (min(now, end_at) - enrollment.started_at).days)
    days_remaining = max(0, (end_at - now).days)

    workouts_logged = WorkoutLog.query.filter(
        WorkoutLog.user_id == enrollment.user_id,
        db.func.datetime(WorkoutLog.completed_at) >= db.func.datetime(enrollment.started_at),
        db.func.datetime(WorkoutLog.completed_at) <= db.func.datetime(end_at),
    ).count()

    target = template["target_workouts"]
    progress_pct = min(100, round((workouts_logged / target) * 100)) if target else 0

    # Expected pace: what fraction of the target you'd need by now to
    # finish on time, assuming a steady rate across the whole challenge.
    expected_by_now = target * (days_elapsed / template["duration_days"]) if template["duration_days"] else 0
    on_track = workouts_logged >= expected_by_now or now >= end_at

    return {
        "enrollment_id": enrollment.id,
        "challenge": template,
        "started_at": enrollment.started_at.isoformat(),
        "ends_at": end_at.isoformat(),
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "workouts_logged": workouts_logged,
        "target_workouts": target,
        "progress_pct": progress_pct,
        "on_track": on_track,
        "is_complete": workouts_logged >= target,
        "is_expired": now >= end_at and workouts_logged < target,
    }


@challenges_bp.get("")
@login_required
def list_challenges(user):
    active = (
        UserChallenge.query.filter_by(user_id=user.id, left_at=None)
        .order_by(UserChallenge.started_at.desc())
        .first()
    )
    return jsonify(
        {
            "templates": CHALLENGES,
            "active": _progress_for(active) if active else None,
        }
    ), 200


@challenges_bp.post("/<challenge_id>/join")
@login_required
def join_challenge(user, challenge_id):
    template = get_challenge(challenge_id)
    if not template:
        return jsonify({"error": "Unknown challenge."}), 404

    existing = UserChallenge.query.filter_by(user_id=user.id, left_at=None).first()
    if existing:
        return jsonify({"error": "You already have an active challenge. Leave it before starting a new one."}), 400

    enrollment = UserChallenge(user_id=user.id, challenge_id=challenge_id)
    db.session.add(enrollment)
    db.session.commit()

    return jsonify(_progress_for(enrollment)), 201


@challenges_bp.post("/leave")
@login_required
def leave_challenge(user):
    existing = UserChallenge.query.filter_by(user_id=user.id, left_at=None).first()
    if not existing:
        return jsonify({"error": "No active challenge."}), 404

    existing.left_at = datetime.utcnow()
    db.session.commit()
    return "", 204
