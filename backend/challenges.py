"""Challenge templates - static data, not a database table, same pattern
as gym_equipment.py.

Progress is tracked purely by counting workouts logged during the
challenge window. We deliberately don't claim to verify *what kind* of
workout was done (e.g. "core-focused") because WorkoutLog only stores a
name snapshot and duration, not structured exercise data - a target we
can't actually verify shouldn't be advertised as tracked.
"""

CHALLENGES = [
    {
        "id": "14-day-kickstart",
        "title": "14-Day Kickstart",
        "description": "A short, low-pressure way to build the habit before committing to something longer.",
        "duration_days": 14,
        "target_workouts": 10,
        "level": "beginner",
    },
    {
        "id": "first-30",
        "title": "First 30",
        "description": "Thirty days, fifteen workouts. Built for building the habit, not breaking yourself.",
        "duration_days": 30,
        "target_workouts": 15,
        "level": "beginner",
    },
    {
        "id": "consistency-sprint",
        "title": "Consistency Sprint",
        "description": "Roughly five sessions a week for a month. For people who've got the habit and want to lock it in.",
        "duration_days": 30,
        "target_workouts": 20,
        "level": "intermediate",
    },
    {
        "id": "iron-discipline",
        "title": "Iron Discipline",
        "description": "Near-daily training for 30 days straight. Not for a first month - for people ready to push.",
        "duration_days": 30,
        "target_workouts": 26,
        "level": "advanced",
    },
]


def get_challenge(challenge_id):
    return next((c for c in CHALLENGES if c["id"] == challenge_id), None)
