from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError

from models import VALID_CATEGORIES, VALID_MUSCLE_GROUPS, VALID_EQUIPMENT, VALID_GOALS


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class ProfileUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=1, max=100))
    age = fields.Integer(allow_none=True, validate=validate.Range(min=10, max=100))
    height_cm = fields.Float(allow_none=True, validate=validate.Range(min=100, max=250))
    weight_kg = fields.Float(allow_none=True, validate=validate.Range(min=30, max=300))
    target_weight_kg = fields.Float(allow_none=True, validate=validate.Range(min=30, max=300))
    target_date = fields.Date(allow_none=True)
    goal = fields.String(validate=validate.OneOf(VALID_GOALS))
    equipment = fields.List(fields.String(validate=validate.OneOf(VALID_EQUIPMENT)))
    focus_areas = fields.List(fields.String(validate=validate.OneOf(VALID_MUSCLE_GROUPS)))

    @validates_schema
    def validate_target(self, data, **kwargs):
        if data.get("target_date") and not data.get("target_weight_kg"):
            raise ValidationError("target_weight_kg is required when target_date is set.", "target_weight_kg")


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.String(dump_only=True)
    name = fields.String()
    age = fields.Integer()
    height_cm = fields.Float()
    weight_kg = fields.Float()
    target_weight_kg = fields.Float()
    target_date = fields.Date()
    goal = fields.String()
    equipment = fields.List(fields.String())
    focus_areas = fields.List(fields.String())
    bmi = fields.Method("get_bmi", dump_only=True)
    is_admin = fields.Boolean(dump_only=True)
    subscription_status = fields.String(dump_only=True)
    subscription_expires_at = fields.DateTime(dump_only=True)

    def get_bmi(self, obj):
        return obj.bmi


class ExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    category = fields.String(required=True, validate=validate.OneOf(VALID_CATEGORIES))
    muscle_group = fields.String(required=True, validate=validate.OneOf(VALID_MUSCLE_GROUPS))
    equipment = fields.String(validate=validate.OneOf(VALID_EQUIPMENT), load_default="none")
    difficulty = fields.String(load_default="beginner")


class WorkoutExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    exercise_id = fields.Integer(required=True)
    exercise_name = fields.Method("get_exercise_name", dump_only=True)
    muscle_group = fields.Method("get_muscle_group", dump_only=True)
    sets = fields.Integer(required=True, validate=validate.Range(min=1))
    reps = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    duration_seconds = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    order_index = fields.Integer()

    def get_exercise_name(self, obj):
        return obj.exercise.name if obj.exercise else None

    def get_muscle_group(self, obj):
        return obj.exercise.muscle_group if obj.exercise else None


class WorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    day_label = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    workout_exercises = fields.List(fields.Nested(WorkoutExerciseSchema), dump_only=True)


class WorkoutLogSchema(Schema):
    id = fields.Integer(dump_only=True)
    workout_id = fields.Integer(allow_none=True)
    workout_name_snapshot = fields.String(dump_only=True)
    completed_at = fields.DateTime(dump_only=True)
    duration_minutes = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    notes = fields.String(allow_none=True, validate=validate.Length(max=500))


class LogWorkoutSchema(Schema):
    workout_id = fields.Integer(allow_none=True)
    workout_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    duration_minutes = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    notes = fields.String(allow_none=True, validate=validate.Length(max=500))


class QuoteSchema(Schema):
    id = fields.Integer(dump_only=True)
    text = fields.String(required=True)
    author = fields.String(allow_none=True)


class STKPushSchema(Schema):
    phone_number = fields.String(required=True, validate=validate.Regexp(r"^254[71]\d{8}$",
                                  error="phone_number must be a Safaricom number in the format 2547XXXXXXXX or 2541XXXXXXXX."))
    plan = fields.String(load_default="monthly", validate=validate.OneOf(["monthly", "annual"]))


register_schema = RegisterSchema()
login_schema = LoginSchema()
profile_update_schema = ProfileUpdateSchema()
user_schema = UserSchema()
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_log_schema = WorkoutLogSchema()
workout_logs_schema = WorkoutLogSchema(many=True)
log_workout_schema = LogWorkoutSchema()
quote_schema = QuoteSchema()
stk_push_schema = STKPushSchema()
