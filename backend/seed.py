#!/usr/bin/env python3
import os

from config import app, db
from models import Exercise, Quote, User

EXERCISES = [
    # name, category, muscle_group, equipment, difficulty
    ("Bodyweight Squat", "strength", "legs", "none", "beginner"),
    ("Walking Lunge", "strength", "legs", "none", "beginner"),
    ("Glute Bridge", "strength", "legs", "none", "beginner"),
    ("Push-Up", "strength", "chest", "none", "beginner"),
    ("Diamond Push-Up", "strength", "chest", "none", "intermediate"),
    ("Chair Tricep Dip", "strength", "arms", "none", "beginner"),
    ("Superman Hold", "strength", "back", "none", "beginner"),
    ("Pike Push-Up", "strength", "shoulders", "none", "intermediate"),
    ("Plank", "strength", "core", "none", "beginner"),
    ("Bicycle Crunch", "strength", "core", "none", "beginner"),
    ("Russian Twist", "strength", "core", "none", "beginner"),
    ("Dumbbell Row", "strength", "back", "dumbbells", "intermediate"),
    ("Dumbbell Shoulder Press", "strength", "shoulders", "dumbbells", "intermediate"),
    ("Goblet Squat", "strength", "legs", "dumbbells", "intermediate"),
    ("Resistance Band Row", "strength", "back", "bands", "beginner"),
    ("Resistance Band Squat", "strength", "legs", "bands", "beginner"),
    ("Jumping Jacks", "cardio", "cardio", "none", "beginner"),
    ("High Knees", "cardio", "cardio", "none", "beginner"),
    ("Mountain Climbers", "cardio", "cardio", "none", "beginner"),
    ("Burpees", "cardio", "cardio", "none", "intermediate"),
    ("Squat Jumps", "cardio", "legs", "none", "intermediate"),
    ("Skater Hops", "cardio", "legs", "none", "intermediate"),
    ("Shadow Boxing", "cardio", "cardio", "none", "beginner"),
    ("Jump Rope", "cardio", "cardio", "none", "beginner"),
    ("Butt Kicks", "cardio", "cardio", "none", "beginner"),
    ("Plank Jacks", "cardio", "core", "none", "intermediate"),
    ("Tuck Jumps", "cardio", "legs", "none", "advanced"),
    ("Wall Sit", "mobility", "legs", "none", "beginner"),
    ("Sun Salutation Flow", "mobility", "full_body", "none", "beginner"),
    ("Cat-Cow Stretch", "mobility", "back", "none", "beginner"),
    ("Hip Flexor Stretch", "mobility", "legs", "none", "beginner"),
    ("Shoulder Rolls & Stretch", "mobility", "shoulders", "none", "beginner"),
    ("Standing Quad Stretch", "mobility", "legs", "none", "beginner"),
    ("Child's Pose Hold", "mobility", "back", "none", "beginner"),
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
        db.create_all()

        print("Clearing existing catalog data...")
        Exercise.query.delete()
        Quote.query.delete()
        db.session.commit()

        print("Seeding exercises...")
        for name, category, muscle_group, equipment, difficulty in EXERCISES:
            db.session.add(
                Exercise(
                    name=name,
                    category=category,
                    muscle_group=muscle_group,
                    equipment=equipment,
                    difficulty=difficulty,
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