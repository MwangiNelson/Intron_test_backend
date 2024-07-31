from flask import request, jsonify
from app import app, db
from models import User
from helpers import generate_password_hash
import jwt
from functools import wraps
from datetime import datetime, timedelta
import bcrypt

# Secret key for JWT
SECRET_KEY = "sample_secret_key"  # Replace with a secure secret key


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            data = jwt.decode(token.split()[1], SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
        except:
            return jsonify({"message": "Token is invalid!"}), 401
        return f(current_user, *args, **kwargs)

    return decorated


@app.route("/users", methods=["GET"])
@token_required
def get_users(current_user):
    users = User.query.all()
    return jsonify(
        [
            {"id": user.id, "username": user.username, "email": user.email}
            for user in users
        ]
    )


@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    if (
        not data
        or "username" not in data
        or "email" not in data
        or "password" not in data
    ):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_user = User(
        username=data["username"], email=data["email"], password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return (
        jsonify(
            {"id": new_user.id, "username": new_user.username, "email": new_user.email}
        ),
        201,
    )


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"message": "Missing email or password"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user:
        return jsonify({"message": "User not found"}), 401

    # Convert input password to bytes
    input_password = data["password"].encode("utf-8")

    # Convert stored hashed password to bytes
    stored_password = user.password.encode("utf-8")

    if bcrypt.checkpw(input_password, stored_password):
        token = jwt.encode(
            {"user_id": user.id, "exp": datetime.utcnow() + timedelta(minutes=30)},
            SECRET_KEY,
        )
        return jsonify({"token": token})

    return jsonify({"message": "Invalid password"}), 401


@app.route("/users/<int:id>", methods=["GET"])
@token_required
def get_user(current_user, id):
    user = User.query.get_or_404(id)
    return jsonify({"id": user.id, "username": user.username, "email": user.email})


@app.route("/users/<int:id>", methods=["PUT"])
@token_required
def update_user(current_user, id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]
    if "password" in data:
        user.password = generate_password_hash(data["password"])
    db.session.commit()
    return jsonify({"id": user.id, "username": user.username, "email": user.email})


@app.route("/users/<int:id>", methods=["DELETE"])
@token_required
def delete_user(current_user, id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return "", 204
