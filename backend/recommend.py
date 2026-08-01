"""Rule-based fitness recommendation engine.

No external ML/API calls - this is a deterministic scoring + selection
algorithm over the exercise catalog, driven by the user's goal, equipment,
and focus areas. Kept rule-based (rather than calling an LLM) so it's
free to run, fast, and fully explainable.
"""
import random
from datetime import date

from models import Exercise

# category mix per goal
GOAL_CATEGORY_WEIGHTS = {
    "lose_fat": {"cardio": 0.5, "strength": 0.3, "mobility": 0.2},
    "build_muscle": {"strength": 0.7, "cardio": 0.2, "mobility": 0.1},
    "endurance": {"cardio": 0.6, "strength": 0.2, "mobility": 0.2},
    "mobility": {"mobility": 0.6, "strength": 0.2, "cardio": 0.2},
}

SAFE_MAX_WEEKLY_RATE_KG = 1.0
EXERCISES_PER_DAY = 5


def bmi_category(bmi):
    if bmi is None:
        return None
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "overweight"
    return "obese"


def target_pace(user):
    """Weekly rate of change needed to hit the user's target weight by
    their target date, or None if either is unset."""
    if not user.target_weight_kg or not user.target_date or not user.weight_kg:
        return None

    days_remaining = (user.target_date - date.today()).days
    if days_remaining <= 0:
        return {"error": "target_date must be in the future."}

    weeks_remaining = max(days_remaining / 7, 1e-6)
    delta_kg = user.weight_kg - user.target_weight_kg  # positive => losing weight
    weekly_rate = round(delta_kg / weeks_remaining, 2)

    return {
        "weeks_remaining": round(weeks_remaining, 1),
        "weekly_rate_kg": weekly_rate,
        "direction": "lose" if delta_kg > 0 else ("gain" if delta_kg < 0 else "maintain"),
        "is_safe_pace": abs(weekly_rate) <= SAFE_MAX_WEEKLY_RATE_KG,
    }


def _usable_equipment(user_equipment):
    equipment = set(user_equipment or [])
    equipment.add("none")  # bodyweight exercises are always usable
    return equipment


def _pick_exercises(pool, category, count, focus_areas, exclude_ids):
    candidates = [e for e in pool if e.category == category and e.id not in exclude_ids]
    if not candidates:
        return []

    if focus_areas:
        focused = [e for e in candidates if e.muscle_group in focus_areas]
        rest = [e for e in candidates if e.muscle_group not in focus_areas]
        random.shuffle(focused)
        random.shuffle(rest)
        ordered = focused + rest
    else:
        ordered = candidates[:]
        random.shuffle(ordered)

    return ordered[:count]


def _sets_reps_for(exercise):
    if exercise.category == "strength":
        return {"sets": 3, "reps": 12, "duration_seconds": None}
    if exercise.category == "cardio":
        return {"sets": 1, "reps": None, "duration_seconds": 40}
    if exercise.category == "mobility":
        return {"sets": 2, "reps": None, "duration_seconds": 30}
    return {"sets": 3, "reps": 12, "duration_seconds": None}


def generate_plan(user, all_exercises, days=3, seed=None):
    """Builds a `days`-long weekly plan tailored to the user's goal,
    equipment, and focus areas. Returns plain dicts (not ORM objects) so
    the plan doesn't need to be persisted before it's shown to the user.
    """
    rng_seed = seed if seed is not None else f"{user.id}-{date.today().isoformat()}"
    random.seed(rng_seed)

    usable = _usable_equipment(user.equipment)
    pool = [e for e in all_exercises if e.equipment in usable]

    weights = GOAL_CATEGORY_WEIGHTS.get(user.goal, GOAL_CATEGORY_WEIGHTS["lose_fat"])
    focus_areas = set(user.focus_areas or [])

    plan_days = []
    used_ids = set()

    for day_num in range(1, days + 1):
        counts = {
            cat: max(1, round(weight * EXERCISES_PER_DAY))
            for cat, weight in weights.items()
        }
        day_exercises = []
        exclude = set(used_ids)

        for category, count in counts.items():
            picked = _pick_exercises(pool, category, count, focus_areas, exclude)
            for ex in picked:
                exclude.add(ex.id)
            day_exercises.extend(picked)

        if len(day_exercises) < EXERCISES_PER_DAY:
            remaining = [e for e in pool if e.id not in exclude]
            random.shuffle(remaining)
            day_exercises.extend(remaining[: EXERCISES_PER_DAY - len(day_exercises)])

        used_ids.update(e.id for e in day_exercises)
        if len(used_ids) >= len(pool) - EXERCISES_PER_DAY:
            used_ids = set()

        plan_days.append(
            {
                "day_number": day_num,
                "focus": ", ".join(sorted(focus_areas)) if focus_areas else "full body",
                "exercises": [
                    {
                        "exercise_id": ex.id,
                        "name": ex.name,
                        "category": ex.category,
                        "muscle_group": ex.muscle_group,
                        **_sets_reps_for(ex),
                    }
                    for ex in day_exercises
                ],
            }
        )

    return {
        "goal": user.goal,
        "bmi": user.bmi,
        "bmi_category": bmi_category(user.bmi),
        "pace": target_pace(user),
        "days": plan_days,
        "guidance": _guidance_text(user),
    }


def _guidance_text(user):
    tips = [
        "Warm up for 5 minutes before each session and stretch afterward.",
        "Aim for consistency over intensity - three solid sessions a week beats one brutal one.",
        "Prioritize sleep and hydration; recovery is when progress actually happens.",
    ]
    if user.goal == "lose_fat":
        tips.append(
            "Pair this plan with a modest, sustainable calorie deficit rather than an extreme cut."
        )
    elif user.goal == "build_muscle":
        tips.append(
            "Make sure you're eating enough protein and total calories to support muscle repair."
        )

    pace = target_pace(user)
    if pace and not pace.get("error") and not pace.get("is_safe_pace"):
        tips.append(
            "Your target date implies a faster rate of change than is generally considered "
            "sustainable - consider extending your timeline for a healthier pace."
        )

    tips.append(
        "This is general guidance, not medical advice - check with a doctor before starting "
        "a new program, especially if you have any existing health conditions."
    )
    return tips
