import os
import logging
from pathlib import Path
from flask import Flask, app, jsonify, render_template
from dotenv import load_dotenv

import db

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


def create_app(test_config=None):
    app = Flask(__name__)

    # Database configuration
    app.config["DATABASE"] = str(DATA_DIR / "gym.db")
    app.config["JSON_SORT_KEYS"] = False

    if test_config:
        app.config.update(test_config)

    # Logging configuration
    logging.basicConfig(
        filename=str(LOG_DIR / "app.log"),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )

    # Register database cleanup
    app.teardown_appcontext(db.close_db)

    # Register member routes
    from routes.member_routes import member_bp
    from routes.membership_routes import membership_bp
    from routes.analytics_routes import analytics_bp
    from routes.workout_routes import workout_bp
    from routes.attendance_routes import attendance_bp
    from routes.workout_progress_routes import progress_bp

    app.register_blueprint(progress_bp, url_prefix="/api")
    app.register_blueprint(attendance_bp, url_prefix="/api")
    app.register_blueprint(workout_bp, url_prefix="/api")
    app.register_blueprint(member_bp, url_prefix="/api")
    app.register_blueprint(membership_bp, url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/api")

    # Home endpoint
    @app.get("/")
    def home():
        return jsonify({
            "message": "Gym Management System API",
            "status": "running"
        })
    # Dashboard endpoint
    @app.get("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    # Health endpoint
    @app.get("/api/health")
    def health():
        return jsonify({"status": "healthy"})

    # Initialize database
    with app.app_context():
        db.init_db()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)