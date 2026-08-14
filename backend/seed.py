#!/usr/bin/env python3
import os

from config import app, db
from models import Exercise, Quote, User

# video_id: verified via real web search (never guessed) - the ID is the
# part after v= in a YouTube URL. None means no video attached yet; add
# one any time by filling in this field for that entry.
#
# tracking_type controls how the exercise is measured and displayed:
#   "reps"     - standard sets x reps (e.g. 3 x 12 squats)
#   "hold"     - an isometric hold, measured in seconds per set (e.g. plank)
#   "duration" - a single continuous timed effort (e.g. 40s of jumping jacks)
EXERCISES = [
    {"name": "Bodyweight Squat", "category": "strength", "muscle_group": "legs", "equipment": "none", "difficulty": "beginner", "tracking_type": "reps", "video_id": "CKcDiJnLaLY"},
    {"name": "Walking Lunge", "category": "strength", "muscle_group": "legs", "equipment": "none", "difficulty": "beginner", "tracking_type": "reps", "video_id": "BenhAbJiTsw"},
    {"name": "Glute Bridge", "category": "strength", "muscle_group": "legs", "equipment": "none", "difficulty": "beginner", "tracking_type": "reps", "video_id": "nuapk_-Q2BI"},
    {"name": "Push-Up", "category": "strength", "muscle_group": "chest", "equipment": "none", "difficulty": "beginner", "tracking_type": "reps", "video_id": "mECzqUIDWfU"},
    {"name": "Diamond Push-Up", "category": "strength", "muscle_group": "chest", "equipment": "none", "difficulty": "advanced", "tracking_type": "reps", "video_id": "2-OFbQ9GLpE"},
    {"name": "Chair Tricep Dip", "category": "strength", "muscle_group": "arms", "equipment": "none", "difficulty": "beginner", "tracking_type": "reps", "video_id": "jDafIn0WMUw"},
    {"name": "Superman Hold", "category": "strength", "muscle_group": "back", "equipment": "none", "difficulty": "beginner", "tracking_type": "hold", "video_id": "LZoWdePF1NQ"},
    {"name": "Pike Push-Up", "category": "strength", "muscle_group": "shoulders", "equipment": "none", "difficulty": "intermediate", "tracking_type": "reps", "video_id": "pHR5yG6xBps"},
    {"name": "Plank", "category": "strength", "muscle_group": "core", "equipment": "none", "difficulty": "beginner", "tracking_type": "hold", "video_id": "mwlp75MS6Rg"},
    {"name": "Bicycle Crunch", "category": "strength", "muscle_group": "core", "equipment": "none", "difficulty": "beginner", "tracking_type": "reps", "video_id": "_O1viJT82S8"},
    {"name": "Russian Twist", "category": "strength", "muscle_group": "core", "equipment": "none", "difficulty": "beginner", "tracking_type": "reps", "video_id": "fPxO-FA8acM"},
    {"name": "Dumbbell Row", "category": "strength", "muscle_group": "back", "equipment": "dumbbells", "difficulty": "intermediate", "tracking_type": "reps", "video_id": "roCP6wCXPqo"},
    {"name": "Dumbbell Shoulder Press", "category": "strength", "muscle_group": "shoulders", "equipment": "dumbbells", "difficulty": "intermediate", "tracking_type": "reps", "video_id": "guW_ENwLOMI"},
    {"name": "Goblet Squat", "category": "strength", "muscle_group": "legs", "equipment": "dumbbells", "difficulty": "intermediate", "tracking_type": "reps", "video_id": "BR4tlEE_A98"},
    {"name": "Resistance Band Row", "category": "strength", "muscle_group": "back", "equipment": "bands", "difficulty": "beginner", "tracking_type": "reps", "video_id": "tcMmJ3c5P8c"},
    {"name": "Resistance Band Squat", "category": "strength", "muscle_group": "legs", "equipment": "bands", "difficulty": "beginner", "tracking_type": "reps", "video_id": "duP-UZsfOaQ"},
    {"name": "Jumping Jacks", "category": "cardio", "muscle_group": "cardio", "equipment": "none", "difficulty": "beginner", "tracking_type": "duration", "video_id": "aknTmegKiIg"},
    {"name": "High Knees", "category": "cardio", "muscle_group": "cardio", "equipment": "none", "difficulty": "beginner", "tracking_type": "duration", "video_id": "OpN2Y712k6Y"},
    {"name": "Mountain Climbers", "category": "cardio", "muscle_group": "cardio", "equipment": "none", "difficulty": "beginner", "tracking_type": "duration", "video_id": "ixxk9Qfn61o"},
    {"name": "Burpees", "category": "cardio", "muscle_group": "cardio", "equipment": "none", "difficulty": "advanced", "tracking_type": "duration", "video_id": "fZx6nxKMq4E"},
    {"name": "Squat Jumps", "category": "cardio", "muscle_group": "legs", "equipment": "none", "difficulty": "intermediate", "tracking_type": "duration", "video_id": "tZSYZdtbONc"},
    {"name": "Skater Hops", "category": "cardio", "muscle_group": "legs", "equipment": "none", "difficulty": "intermediate", "tracking_type": "duration", "video_id": "9_jLW6VkU8A"},
    {"name": "Shadow Boxing", "category": "cardio", "muscle_group": "cardio", "equipment": "none", "difficulty": "beginner", "tracking_type": "duration", "video_id": "Q5WrJoYhpHE"},
    {"name": "Jump Rope", "category": "cardio", "muscle_group": "cardio", "equipment": "none", "difficulty": "beginner", "tracking_type": "duration", "video_id": "E6v_VcZ6qDQ"},
    {"name": "Butt Kicks", "category": "cardio", "muscle_group": "cardio", "equipment": "none", "difficulty": "beginner", "tracking_type": "duration", "video_id": "oMW59TKZvaI"},
    {"name": "Plank Jacks", "category": "cardio", "muscle_group": "core", "equipment": "none", "difficulty": "intermediate", "tracking_type": "duration", "video_id": "8Do3ssZ23Mc"},
    {"name": "Tuck Jumps", "category": "cardio", "muscle_group": "legs", "equipment": "none", "difficulty": "advanced", "tracking_type": "duration", "video_id": "-bnJGikRGsM"},
    {"name": "Wall Sit", "category": "mobility", "muscle_group": "legs", "equipment": "none", "difficulty": "beginner", "tracking_type": "hold", "video_id": "JQ2JBphtUk8"},
    {"name": "Sun Salutation Flow", "category": "mobility", "muscle_group": "full_body", "equipment": "none", "difficulty": "beginner", "tracking_type": "duration", "video_id": "UPszTB6UzaA"},
    {"name": "Cat-Cow Stretch", "category": "mobility", "muscle_group": "back", "equipment": "none", "difficulty": "beginner", "tracking_type": "reps", "video_id": "xyNwxiuERXc"},
    {"name": "Hip Flexor Stretch", "category": "mobility", "muscle_group": "legs", "equipment": "none", "difficulty": "beginner", "tracking_type": "hold", "video_id": "KT0HlPGCl6k"},
    {"name": "Shoulder Rolls & Stretch", "category": "mobility", "muscle_group": "shoulders", "equipment": "none", "difficulty": "beginner", "tracking_type": "reps", "video_id": "X7NtgY9kCCM"},
    {"name": "Standing Quad Stretch", "category": "mobility", "muscle_group": "legs", "equipment": "none", "difficulty": "beginner", "tracking_type": "hold", "video_id": "kia2OzZiwqw"},
    {"name": "Child's Pose Hold", "category": "mobility", "muscle_group": "back", "equipment": "none", "difficulty": "beginner", "tracking_type": "hold", "video_id": "_ZX_zTOBgp8"},
]

QUOTES = [
    ("The only bad workout is the one that didn't happen.", None),
    ("Discipline is choosing between what you want now and what you want most.", None),
    ("Small consistent steps beat occasional heroics.", None),
    ("You don't have to be extreme, just consistent.", None),
    ("Your body can stand almost anything. It's your mind you have to convince.", None),
    ("Progress, not perfection.", None),
    ("Every session you show up for is a vote for the person you're becoming.", None),
    ("The pain of discipline is far less than the pain of regret.", None),
    ("Strength doesn't come from what you can do. It comes from overcoming what you thought you couldn't.", None),
    ("Motivation gets you started. Habit keeps you going.", None),
    ("You are one workout away from a good mood.", None),
    ("Sweat is just fat crying.", None),
    ("Fall in love with the process, and the results will follow.", None),
    ("Nguvu ni kujenga siku moja moja - strength is built one day at a time.", None),
    ("Don't count the days, make the days count.", None),
]


def seed():
    with app.app_context():
        print("Clearing existing catalog data...")
        Exercise.query.delete()
        Quote.query.delete()
        db.session.commit()

        print("Seeding exercises...")
        for ex in EXERCISES:
            db.session.add(
                Exercise(
                    name=ex["name"],
                    category=ex["category"],
                    muscle_group=ex["muscle_group"],
                    equipment=ex["equipment"],
                    difficulty=ex["difficulty"],
                    tracking_type=ex["tracking_type"],
                    video_id=ex["video_id"],
                )
            )

        print("Seeding quotes...")
        for text, author in QUOTES:
            db.session.add(Quote(text=text, author=author))

        db.session.commit()

        admin_email = os.environ.get("ADMIN_EMAIL", "admin@nguvufit.com")
        admin_password = os.environ.get("ADMIN_PASSWORD", "changeme123")
        if not User.query.filter_by(email=admin_email).first():
            print(f"Seeding admin account ({admin_email})...")
            admin = User(email=admin_email, name="Admin", is_admin=True)
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()

        print(
            f"Done. Seeded {len(EXERCISES)} exercises, {len(QUOTES)} quotes, admin account ready."
        )


if __name__ == "__main__":
    seed()