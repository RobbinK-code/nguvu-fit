import pytest
from datetime import datetime, timedelta

from app import app
from config import db, limiter
from models import Exercise, Quote, User


@pytest.fixture
def client():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    # Flask's test client sends every request from the same fake IP, so
    # without this, all tests share one rate-limit bucket and later tests
    # start failing once earlier ones exhaust it - not a real-world bug,
    # just a test-environment artifact.
    limiter.enabled = False

    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add_all(
            [
                Exercise(name="Squat", category="strength", muscle_group="legs", equipment="none"),
                Exercise(name="Push-Up", category="strength", muscle_group="chest", equipment="none"),
                Exercise(name="Burpees", category="cardio", muscle_group="cardio", equipment="none"),
                Exercise(name="Plank", category="mobility", muscle_group="core", equipment="none"),
                Exercise(name="Dumbbell Row", category="strength", muscle_group="back", equipment="dumbbells"),
                Quote(text="Show up.", author=None),
            ]
        )
        db.session.commit()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def register(client, email="user@test.com"):
    resp = client.post("/auth/register", json={"email": email, "password": "password123", "name": "Test"})
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client):
    resp = client.post("/auth/register", json={"email": "a@b.com", "password": "password123", "name": "A"})
    assert resp.status_code == 201

    resp = client.post("/auth/login", json={"email": "a@b.com", "password": "password123"})
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "password123", "name": "A"})
    resp = client.post("/auth/login", json={"email": "a@b.com", "password": "wrong"})
    assert resp.status_code == 401


def test_duplicate_registration_rejected(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "password123", "name": "A"})
    resp = client.post("/auth/register", json={"email": "a@b.com", "password": "password123", "name": "A"})
    assert resp.status_code == 400


def test_short_password_rejected(client):
    resp = client.post("/auth/register", json={"email": "a@b.com", "password": "short", "name": "A"})
    assert resp.status_code == 400


def test_profile_update_and_bmi(client):
    headers = register(client)
    resp = client.patch(
        "/profile",
        json={"height_cm": 180, "weight_kg": 80, "goal": "lose_fat", "equipment": ["none"]},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.get_json()["bmi"] == 24.7


def test_plan_requires_height_and_weight(client):
    headers = register(client)
    resp = client.get("/plan", headers=headers)
    assert resp.status_code == 400


def test_plan_generation(client):
    headers = register(client)
    client.patch("/profile", json={"height_cm": 180, "weight_kg": 80, "equipment": ["none"]}, headers=headers)
    resp = client.get("/plan?days=2", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["days"]) == 2
    assert data["bmi_category"] == "overweight" or data["bmi_category"] == "normal"


def test_quote_of_the_day(client):
    headers = register(client)
    resp = client.get("/quotes/today", headers=headers)
    assert resp.status_code == 200
    assert "text" in resp.get_json()


def test_log_and_fetch_workout(client):
    headers = register(client)
    resp = client.post("/logs", json={"workout_name": "Leg Day", "duration_minutes": 30}, headers=headers)
    assert resp.status_code == 201

    resp = client.get("/logs", headers=headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_non_admin_cannot_access_admin_routes(client):
    headers = register(client)
    resp = client.get("/admin/users", headers=headers)
    assert resp.status_code == 403


def test_admin_can_list_users(client):
    with app.app_context():
        admin = User(email="admin@test.com", name="Admin", is_admin=True)
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()

    resp = app.test_client().post("/auth/login", json={"email": "admin@test.com", "password": "password123"})
    headers = {"Authorization": f"Bearer {resp.get_json()['token']}"}

    resp = app.test_client().get("/admin/users", headers=headers)
    assert resp.status_code == 200


def test_subscribe_fails_gracefully_without_mpesa_config(client):
    headers = register(client)
    resp = client.post(
        "/payments/subscribe", json={"phone_number": "254712345678", "plan": "monthly"}, headers=headers
    )
    assert resp.status_code == 501


def test_admin_has_premium_without_paying(client):
    with app.app_context():
        admin = User(email="admin2@test.com", name="Admin", is_admin=True)
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()

    resp = app.test_client().post("/auth/login", json={"email": "admin2@test.com", "password": "password123"})
    headers = {"Authorization": f"Bearer {resp.get_json()['token']}"}

    me = app.test_client().get("/auth/me", headers=headers)
    assert me.get_json()["has_premium"] is True
    assert me.get_json()["subscription_status"] == "free"


def test_admin_can_grant_and_revoke_subscription(client):
    with app.app_context():
        admin = User(email="admin3@test.com", name="Admin", is_admin=True)
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()

    admin_resp = app.test_client().post(
        "/auth/login", json={"email": "admin3@test.com", "password": "password123"}
    )
    admin_headers = {"Authorization": f"Bearer {admin_resp.get_json()['token']}"}

    user_headers = register(client, email="regular@test.com")
    me = app.test_client().get("/auth/me", headers=user_headers).get_json()
    user_id = me["id"]

    grant = app.test_client().patch(
        f"/admin/users/{user_id}/subscription", json={"action": "grant", "days": 30}, headers=admin_headers
    )
    assert grant.status_code == 200
    assert grant.get_json()["has_premium"] is True

    revoke = app.test_client().patch(
        f"/admin/users/{user_id}/subscription", json={"action": "revoke"}, headers=admin_headers
    )
    assert revoke.status_code == 200
    assert revoke.get_json()["has_premium"] is False


def test_free_user_gets_limited_equipment_list(client):
    headers = register(client)
    resp = client.get("/equipment?muscle_group=legs", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["is_premium"] is False
    assert len(data["equipment"]) == 1


def test_admin_gets_full_equipment_list(client):
    with app.app_context():
        admin = User(email="admin4@test.com", name="Admin", is_admin=True)
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()

    resp = app.test_client().post("/auth/login", json={"email": "admin4@test.com", "password": "password123"})
    headers = {"Authorization": f"Bearer {resp.get_json()['token']}"}

    resp = app.test_client().get("/equipment?muscle_group=legs", headers=headers)
    data = resp.get_json()
    assert data["is_premium"] is True
    assert len(data["equipment"]) > 1


def test_free_user_cannot_refresh_plan(client):
    headers = register(client)
    client.patch("/profile", json={"height_cm": 180, "weight_kg": 80, "equipment": ["none"]}, headers=headers)
    resp = client.get("/plan?days=2&refresh=1", headers=headers)
    assert resp.status_code == 402


def test_premium_user_can_refresh_plan(client):
    with app.app_context():
        admin = User(email="admin5@test.com", name="Admin", is_admin=True)
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()

    resp = app.test_client().post("/auth/login", json={"email": "admin5@test.com", "password": "password123"})
    headers = {"Authorization": f"Bearer {resp.get_json()['token']}"}
    app.test_client().patch(
        "/profile", json={"height_cm": 180, "weight_kg": 80, "equipment": ["none"]}, headers=headers
    )
    resp = app.test_client().get("/plan?days=2&refresh=1", headers=headers)
    assert resp.status_code == 200


def test_free_user_capped_at_three_day_plan(client):
    headers = register(client)
    client.patch("/profile", json={"height_cm": 180, "weight_kg": 80, "equipment": ["none"]}, headers=headers)
    resp = client.get("/plan?days=5", headers=headers)
    assert resp.status_code == 402


def test_premium_user_can_get_longer_plan(client):
    with app.app_context():
        admin = User(email="admin6@test.com", name="Admin", is_admin=True)
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()

    resp = app.test_client().post("/auth/login", json={"email": "admin6@test.com", "password": "password123"})
    headers = {"Authorization": f"Bearer {resp.get_json()['token']}"}
    app.test_client().patch(
        "/profile", json={"height_cm": 180, "weight_kg": 80, "equipment": ["none"]}, headers=headers
    )
    resp = app.test_client().get("/plan?days=5", headers=headers)
    assert resp.status_code == 200
    assert len(resp.get_json()["days"]) == 5


def test_free_user_cannot_access_metrics(client):
    headers = register(client)
    resp = client.get("/metrics", headers=headers)
    assert resp.status_code == 402
    resp = client.post("/metrics", json={"weight_kg": 80}, headers=headers)
    assert resp.status_code == 402


def test_premium_user_can_log_and_fetch_metrics(client):
    with app.app_context():
        admin = User(email="admin7@test.com", name="Admin", is_admin=True)
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()

    resp = app.test_client().post("/auth/login", json={"email": "admin7@test.com", "password": "password123"})
    headers = {"Authorization": f"Bearer {resp.get_json()['token']}"}

    resp = app.test_client().post(
        "/metrics", json={"weight_kg": 82.5, "waist_cm": 90}, headers=headers
    )
    assert resp.status_code == 201
    assert resp.get_json()["weight_kg"] == 82.5

    # weight_kg should sync onto the user's profile for BMI purposes
    me = app.test_client().get("/auth/me", headers=headers).get_json()
    assert me["weight_kg"] == 82.5

    resp = app.test_client().get("/metrics", headers=headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_metric_entry_requires_at_least_one_measurement(client):
    with app.app_context():
        admin = User(email="admin8@test.com", name="Admin", is_admin=True)
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()

    resp = app.test_client().post("/auth/login", json={"email": "admin8@test.com", "password": "password123"})
    headers = {"Authorization": f"Bearer {resp.get_json()['token']}"}

    resp = app.test_client().post("/metrics", json={"notes": "no numbers here"}, headers=headers)
    assert resp.status_code == 400


def test_forgot_password_returns_generic_message_for_unknown_email(client):
    resp = client.post("/auth/forgot-password", json={"email": "nobody@test.com"})
    assert resp.status_code == 200
    assert "If an account exists" in resp.get_json()["message"]


def test_forgot_password_generates_token_for_real_user(client):
    client.post("/auth/register", json={"email": "reset@test.com", "password": "password123", "name": "R"})

    resp = client.post("/auth/forgot-password", json={"email": "reset@test.com"})
    assert resp.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="reset@test.com").first()
        assert user.reset_token is not None
        assert user.reset_token_expires_at is not None


def test_reset_password_with_valid_token(client):
    client.post("/auth/register", json={"email": "reset2@test.com", "password": "password123", "name": "R"})

    with app.app_context():
        user = User.query.filter_by(email="reset2@test.com").first()
        token = user.generate_reset_token()
        db.session.commit()

    resp = client.post("/auth/reset-password", json={"token": token, "new_password": "newpassword456"})
    assert resp.status_code == 200

    # old password should no longer work, new one should
    resp = client.post("/auth/login", json={"email": "reset2@test.com", "password": "password123"})
    assert resp.status_code == 401
    resp = client.post("/auth/login", json={"email": "reset2@test.com", "password": "newpassword456"})
    assert resp.status_code == 200


def test_reset_password_with_invalid_token_rejected(client):
    resp = client.post("/auth/reset-password", json={"token": "not-a-real-token", "new_password": "newpassword456"})
    assert resp.status_code == 400


def test_reset_password_with_expired_token_rejected(client):
    client.post("/auth/register", json={"email": "reset3@test.com", "password": "password123", "name": "R"})

    with app.app_context():
        user = User.query.filter_by(email="reset3@test.com").first()
        user.generate_reset_token()
        user.reset_token_expires_at = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()
        token = user.reset_token

    resp = client.post("/auth/reset-password", json={"token": token, "new_password": "newpassword456"})
    assert resp.status_code == 400


def test_reset_token_cannot_be_reused(client):
    client.post("/auth/register", json={"email": "reset4@test.com", "password": "password123", "name": "R"})

    with app.app_context():
        user = User.query.filter_by(email="reset4@test.com").first()
        token = user.generate_reset_token()
        db.session.commit()

    first = client.post("/auth/reset-password", json={"token": token, "new_password": "newpassword456"})
    assert first.status_code == 200

    second = client.post("/auth/reset-password", json={"token": token, "new_password": "anotherpassword789"})
    assert second.status_code == 400


def test_young_user_never_gets_advanced_exercises_even_on_legendary_tier(client):
    headers = register(client, email="kid@test.com")
    client.patch(
        "/profile",
        json={"age": 12, "height_cm": 150, "weight_kg": 45, "equipment": ["none"], "fitness_tier": "legendary"},
        headers=headers,
    )
    resp = client.get("/plan?days=3", headers=headers)
    assert resp.status_code == 200
    difficulties = {ex["difficulty"] for day in resp.get_json()["days"] for ex in day["exercises"]}
    assert "advanced" not in difficulties


def test_adult_beginner_tier_gets_lower_volume_than_legendary(client):
    headers_beginner = register(client, email="beginner@test.com")
    client.patch(
        "/profile",
        json={"age": 30, "height_cm": 180, "weight_kg": 80, "equipment": ["none"], "fitness_tier": "beginner"},
        headers=headers_beginner,
    )
    beginner_plan = client.get("/plan?days=1", headers=headers_beginner).get_json()
    beginner_reps_exercise = next(
        ex for day in beginner_plan["days"] for ex in day["exercises"] if ex["tracking_type"] == "reps"
    )

    headers_legendary = register(client, email="legendary@test.com")
    client.patch(
        "/profile",
        json={"age": 30, "height_cm": 180, "weight_kg": 80, "equipment": ["none"], "fitness_tier": "legendary"},
        headers=headers_legendary,
    )
    legendary_plan = client.get("/plan?days=1", headers=headers_legendary).get_json()
    legendary_reps_exercise = next(
        ex for day in legendary_plan["days"] for ex in day["exercises"] if ex["tracking_type"] == "reps"
    )

    assert legendary_reps_exercise["reps"] > beginner_reps_exercise["reps"]


def test_hold_exercises_use_duration_not_reps(client):
    headers = register(client, email="holdtest@test.com")
    client.patch(
        "/profile",
        json={"age": 30, "height_cm": 180, "weight_kg": 80, "equipment": ["none"], "focus_areas": ["core"]},
        headers=headers,
    )
    resp = client.get("/plan?days=3", headers=headers)
    plan = resp.get_json()
    hold_exercises = [ex for day in plan["days"] for ex in day["exercises"] if ex["tracking_type"] == "hold"]
    for ex in hold_exercises:
        assert ex["reps"] is None
        assert ex["duration_seconds"] is not None and ex["duration_seconds"] > 0


def test_export_includes_profile_and_history(client):
    headers = register(client, email="exportme@test.com")
    client.patch("/profile", json={"height_cm": 180, "weight_kg": 80}, headers=headers)
    client.post("/logs", json={"workout_name": "Day 1", "duration_minutes": 30}, headers=headers)

    resp = client.get("/profile/export", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["profile"]["email"] == "exportme@test.com"
    assert len(data["workout_logs"]) == 1
    assert "body_metric_logs" in data
    assert "payments" in data


def test_delete_account_requires_correct_password(client):
    headers = register(client, email="deleteme@test.com")
    resp = client.delete("/profile", json={"password": "wrongpassword"}, headers=headers)
    assert resp.status_code == 401

    # account should still exist and be usable
    resp = client.post("/auth/login", json={"email": "deleteme@test.com", "password": "password123"})
    assert resp.status_code == 200


def test_delete_account_succeeds_with_correct_password(client):
    headers = register(client, email="deleteforreal@test.com")
    resp = client.delete("/profile", json={"password": "password123"}, headers=headers)
    assert resp.status_code == 204

    resp = client.post(
        "/auth/login", json={"email": "deleteforreal@test.com", "password": "password123"}
    )
    assert resp.status_code == 401


def test_rate_limit_blocks_excessive_login_attempts(client):
    # This test deliberately re-enables the limiter (disabled globally for
    # the rest of the suite) to prove it actually functions.
    limiter.enabled = True
    try:
        client.post("/auth/register", json={"email": "ratelimited@test.com", "password": "password123", "name": "R"})
        responses = [
            client.post("/auth/login", json={"email": "ratelimited@test.com", "password": "wrong"})
            for _ in range(11)
        ]
        assert any(r.status_code == 429 for r in responses)
    finally:
        limiter.enabled = False
