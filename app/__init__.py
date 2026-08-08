import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import Config
from extensions import db, login_manager, migrate, cors

def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    # Ensure directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["REPORTS_FOLDER"], exist_ok=True)
    os.makedirs(app.config["CHARTS_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    from models.user import User
    from models.settings import UserSettings
    from models.resume import Resume
    from models.report import Report
    from models.criteria import Criteria
    from models.log import AnalysisLog

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.upload import upload_bp
    from routes.analysis import analysis_bp
    from routes.criteria import criteria_bp
    from routes.history import history_bp
    from routes.reports import reports_bp
    from routes.admin import admin_bp
    from routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(criteria_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(settings_bp)

    # Frontend Page Views
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/report")
    @app.route("/report/<int:report_id>")
    def report_view(report_id=None):
        return render_template("report.html", report_id=report_id)

    @app.route("/admin")
    def admin_view():
        return render_template("admin.html")

    # Create tables automatically and run column migrations
    with app.app_context():
        db.create_all()
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('users')]
            with db.engine.begin() as conn:
                if 'phone' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(50)"))
                if 'professional_title' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN professional_title VARCHAR(100)"))
                if 'location' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN location VARCHAR(100)"))
                if 'updated_at' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME"))
        except Exception as e:
            app.logger.warning(f"Schema migration note: {e}")

    return app
