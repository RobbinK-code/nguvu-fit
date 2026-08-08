from flask import jsonify

from config import app
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.exercises import exercises_bp
from routes.plan import plan_bp
from routes.logs import logs_bp
from routes.quotes import quotes_bp
from routes.payments import payments_bp
from routes.admin import admin_bp
from routes.equipment import equipment_bp
from routes.metrics import metrics_bp

for bp in (auth_bp, profile_bp, exercises_bp, plan_bp, logs_bp, quotes_bp, payments_bp, admin_bp, equipment_bp, metrics_bp):
    app.register_blueprint(bp)


@app.get("/")
def index():
    return jsonify({"message": "Nguvu Fit API", "status": "ok"})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found."}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error."}), 500


if __name__ == "__main__":
    app.run(port=5555, debug=True)
