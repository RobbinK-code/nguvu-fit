from datetime import datetime, date

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

from config import db

VALID_CATEGORIES = ("cardio", "strength", "mobility", "balance")
VALID_MUSCLE_GROUPS = (
    "legs", "chest", "back", "shoulders", "arms", "core", "full_body", "cardio",
)
VALID_EQUIPMENT = ("none", "dumbbells", "bands", "full_gym")
VALID_GOALS = ("lose_fat", "build_muscle", "endurance", "mobility")
VALID_SUBSCRIPTION_STATUSES = ("free", "active", "expired")


class User(db.Model):
    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint("height_cm IS NULL OR height_cm > 0", name="height_positive"),
        CheckConstraint("weight_kg IS NULL OR weight_kg > 0", name="weight_positive"),
        CheckConstraint("age IS NULL OR age > 0", name="age_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)

    age = db.Column(db.Integer)
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    target_weight_kg = db.Column(db.Float)
    target_date = db.Column(db.Date)

    goal = db.Column(db.String, default="lose_fat", nullable=False)
    equipment = db.Column(db.JSON, default=list)
    focus_areas = db.Column(db.JSON, default=list)

    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    subscription_status = db.Column(db.String, default="free", nullable=False)
    subscription_expires_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    workout_logs = db.relationship("WorkoutLog", back_populates="user", cascade="all, delete-orphan")
    payments = db.relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    body_metric_logs = db.relationship("BodyMetricLog", back_populates="user", cascade="all, delete-orphan")

    @validates("email")
    def validate_email(self, key, value):
        if not value or "@" not in value:
            raise ValueError("A valid email is required.")
        return value.strip().lower()

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Name is required.")
        return value.strip()

    @validates("goal")
    def validate_goal(self, key, value):
        if value not in VALID_GOALS:
            raise ValueError(f"goal must be one of {VALID_GOALS}.")
        return value

    @validates("subscription_status")
    def validate_subscription_status(self, key, value):
        if value not in VALID_SUBSCRIPTION_STATUSES:
            raise ValueError(f"subscription_status must be one of {VALID_SUBSCRIPTION_STATUSES}.")
        return value

    def set_password(self, raw_password):
        if not raw_password or len(raw_password) < 8:
            raise ValueError("Password must be at least 8 characters.")
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    @property
    def bmi(self):
        if not self.height_cm or not self.weight_kg:
            return None
        h_m = self.height_cm / 100
        return round(self.weight_kg / (h_m * h_m), 1)

    def has_active_subscription(self):
        if self.is_admin:
            return True
        if self.subscription_status != "active":
            return False
        if self.subscription_expires_at and self.subscription_expires_at < datetime.utcnow():
            return False
        return True

    def __repr__(self):
        return f"<User {self.id}: {self.email}>"


class Exercise(db.Model):
    __tablename__ = "exercises"

    __table_args__ = (
        UniqueConstraint("name", name="uq_exercises_name"),
        CheckConstraint("length(name) > 0", name="name_not_empty"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    muscle_group = db.Column(db.String, nullable=False)
    equipment = db.Column(db.String, default="none", nullable=False)
    difficulty = db.Column(db.String, default="beginner", nullable=False)

    workout_exercises = db.relationship("WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan")

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name must not be empty.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        if value not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}.")
        return value

    @validates("muscle_group")
    def validate_muscle_group(self, key, value):
        if value not in VALID_MUSCLE_GROUPS:
            raise ValueError(f"muscle_group must be one of {VALID_MUSCLE_GROUPS}.")
        return value

    @validates("equipment")
    def validate_equipment(self, key, value):
        if value not in VALID_EQUIPMENT:
            raise ValueError(f"equipment must be one of {VALID_EQUIPMENT}.")
        return value

    def __repr__(self):
        return f"<Exercise {self.id}: {self.name}>"


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    name = db.Column(db.String, nullable=False)
    day_label = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan",
        order_by="WorkoutExercise.order_index",
    )
    logs = db.relationship("WorkoutLog", back_populates="workout", cascade="all, delete-orphan")

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Workout name must not be empty.")
        return value.strip()

    def __repr__(self):
        return f"<Workout {self.id}: {self.name}>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    __table_args__ = (
        CheckConstraint("sets > 0", name="sets_positive"),
        CheckConstraint("(reps IS NULL) OR (reps > 0)", name="reps_positive_if_present"),
        CheckConstraint(
            "(duration_seconds IS NULL) OR (duration_seconds > 0)",
            name="duration_positive_if_present",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    order_index = db.Column(db.Integer, default=0, nullable=False)

    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("sets")
    def validate_sets(self, key, value):
        if value is None or value <= 0:
            raise ValueError("sets must be a positive integer.")
        return value

    def __repr__(self):
        return f"<WorkoutExercise workout={self.workout_id} exercise={self.exercise_id}>"


class WorkoutLog(db.Model):
    """A record of a user completing a workout - powers the history view."""

    __tablename__ = "workout_logs"

    __table_args__ = (
        CheckConstraint(
            "duration_minutes IS NULL OR duration_minutes > 0", name="duration_positive"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"))
    workout_name_snapshot = db.Column(db.String, nullable=False)
    completed_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    duration_minutes = db.Column(db.Integer)
    notes = db.Column(db.String)

    user = db.relationship("User", back_populates="workout_logs")
    workout = db.relationship("Workout", back_populates="logs")

    def __repr__(self):
        return f"<WorkoutLog user={self.user_id} workout={self.workout_name_snapshot}>"


class Quote(db.Model):
    __tablename__ = "quotes"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    author = db.Column(db.String)

    @validates("text")
    def validate_text(self, key, value):
        if not value or not value.strip():
            raise ValueError("Quote text must not be empty.")
        return value.strip()


class Payment(db.Model):
    """One M-Pesa STK Push attempt/result, tied to a subscription purchase."""

    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    checkout_request_id = db.Column(db.String, unique=True)
    merchant_request_id = db.Column(db.String)
    mpesa_receipt = db.Column(db.String)
    status = db.Column(db.String, default="pending", nullable=False)  # pending/success/failed
    plan = db.Column(db.String, default="monthly", nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    user = db.relationship("User", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.id} user={self.user_id} status={self.status}>"


class BodyMetricLog(db.Model):
    """A premium-only progress entry: weight and/or body measurements at a
    point in time, so subscribers can chart real trends rather than just
    seeing a single static weight field on their profile."""

    __tablename__ = "body_metric_logs"

    __table_args__ = (
        CheckConstraint("weight_kg IS NULL OR weight_kg > 0", name="weight_positive"),
        CheckConstraint("chest_cm IS NULL OR chest_cm > 0", name="chest_positive"),
        CheckConstraint("waist_cm IS NULL OR waist_cm > 0", name="waist_positive"),
        CheckConstraint("hips_cm IS NULL OR hips_cm > 0", name="hips_positive"),
        CheckConstraint("arm_cm IS NULL OR arm_cm > 0", name="arm_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    weight_kg = db.Column(db.Float)
    chest_cm = db.Column(db.Float)
    waist_cm = db.Column(db.Float)
    hips_cm = db.Column(db.Float)
    arm_cm = db.Column(db.Float)
    notes = db.Column(db.String)

    recorded_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    user = db.relationship("User", back_populates="body_metric_logs")

    def __repr__(self):
        return f"<BodyMetricLog user={self.user_id} at={self.recorded_at}>"
