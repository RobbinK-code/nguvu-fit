import pytest

from app import app
from config import db
from models import Exercise, Quote, User


@pytest.fixture
def client():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

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
