from flask import Blueprint, request, jsonify
from extensions import db, bcrypt
from auth.models import User
from flask_jwt_extended import create_access_token
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os


auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.json
    email = data["email"]
    username = data["username"]
    password = data["password"]


    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    
    user = User(email=email, username=username, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user_id": user.id})

@auth_bp.post("/login")
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user_id": user.id})



#google oauth2 login
@auth_bp.post("/google")
def google_login():
    """
    Login/register with Google OAuth2.
    Frontend should send: { "token": "<Google ID token>" }
    """
    data = request.json
    token = data.get("token")

    if not token:
        return jsonify({"error": "Token is required"}), 400

    try:
        # Verify Google token
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), os.getenv("GOOGLE_CLIENT_ID"))
        email = idinfo.get("email")
        username = idinfo.get("name") or email.split("@")[0]

        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user without password
            user = User(email=email, username=username, password_hash=None)
            db.session.add(user)
            db.session.commit()

        jwt_token = create_access_token(identity=user.id)
        return jsonify({"token": jwt_token, "user_id": user.id})

    except ValueError:
        return jsonify({"error": "Invalid Google token"}), 401