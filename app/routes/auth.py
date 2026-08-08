import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User
from utils.validators import validate_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/auth/supabase-config", methods=["GET"])
def supabase_config():
    supabase_url = current_app.config.get("SUPABASE_URL", "")
    supabase_key = current_app.config.get("SUPABASE_PUBLISHABLE_KEY", "")
    return jsonify({
        "success": True,
        "supabase_url": supabase_url,
        "supabase_publishable_key": supabase_key
    })

@auth_bp.route("/api/auth/supabase-sync", methods=["POST"])
def supabase_sync():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    name = data.get("name", "").strip() or (email.split("@")[0] if email else "Supabase User")
    supabase_id = data.get("supabase_id", "")

    if not email:
        return jsonify({"success": False, "message": "User email is required from Supabase."}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        try:
            role = "admin" if User.query.count() == 0 else "user"
            user = User(
                email=email,
                name=name,
                role=role,
                google_id=f"supabase_{supabase_id}" if supabase_id else "supabase_oauth"
            )
            user.set_password(secrets.token_hex(12))
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({"success": False, "message": "Failed to create or sync user profile."}), 500

    login_user(user)
    return jsonify({
        "success": True,
        "message": "Supabase authentication synced successfully.",
        "user": user.to_dict()
    })

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or request.form
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    if not email or not password or not name:
        return jsonify({"success": False, "message": "Email, password, and name are required."}), 400

    if not validate_email(email):
        return jsonify({"success": False, "message": "Invalid email format."}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"success": False, "message": "User with this email already exists."}), 400

    # First registered user becomes admin automatically
    role = "admin" if User.query.count() == 0 else "user"

    user = User(email=email, name=name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return jsonify({"success": True, "message": "Registration successful.", "user": user.to_dict()})

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or request.form
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"success": False, "message": "Invalid credentials."}), 401

    login_user(user)
    return jsonify({"success": True, "message": "Login successful.", "user": user.to_dict()})

@auth_bp.route("/api/auth/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return jsonify({"success": True, "message": "Logged out successfully."})

@auth_bp.route("/api/auth/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or request.form
    email = data.get("email", "").strip().lower()
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"success": False, "message": "If an account exists with this email, a reset link has been issued."})

    token = secrets.token_hex(16)
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Password reset token generated.",
        "reset_token": token,
        "reset_url": url_for("auth.reset_password_page", token=token, _external=True)
    })

@auth_bp.route("/api/auth/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or request.form
    token = data.get("token", "")
    new_password = data.get("new_password", "")

    if not token or not new_password:
        return jsonify({"success": False, "message": "Token and new password required."}), 400

    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400

    user.set_password(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()

    return jsonify({"success": True, "message": "Password reset successful. Please login."})

@auth_bp.route("/api/auth/google", methods=["POST"])
def google_login():
    data = request.get_json() or {}
    email = data.get("email", "google.user@example.com").lower()
    name = data.get("name", "Google User")
    
    user = User.query.filter_by(email=email).first()
    if not user:
        try:
            role = "admin" if User.query.count() == 0 else "user"
            user = User(email=email, name=name, role=role, google_id="google_oauth_12345")
            user.set_password(secrets.token_hex(8))
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({"success": False, "message": "Failed to authenticate Google user."}), 500

    login_user(user)
    return jsonify({"success": True, "message": "Google Login successful.", "user": user.to_dict()})

@auth_bp.route("/api/auth/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        data = request.get_json() or request.form
        name = data.get("name", "").strip()
        if name:
            current_user.name = name
            db.session.commit()
        return jsonify({"success": True, "message": "Profile updated.", "user": current_user.to_dict()})
    return jsonify({"success": True, "user": current_user.to_dict()})

@auth_bp.route("/reset-password/<token>")
def reset_password_page(token):
    return render_template("index.html", reset_token=token)
