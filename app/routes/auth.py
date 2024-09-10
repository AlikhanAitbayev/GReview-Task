from flask import Blueprint, request, jsonify, Response
from app.models import Users, db
from app.services.auth_service import encode_auth_token

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/auth/signup", methods=["POST"])
def signup() -> Response:
    data = request.get_json()
    user = Users(username=data["username"], email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    auth_token = encode_auth_token(user.id)
    return jsonify({"token": auth_token}), 201

@auth_blueprint.route("/auth/login", methods=["POST"])
def login() -> Response:
    data = request.get_json()
    user = Users.query.filter_by(email=data["email"]).first()
    if user and user.check_password(data["password"]):
        auth_token = encode_auth_token(user.id)
        return jsonify({"token": auth_token})
    return jsonify({"message": "Invalid credentials"}), 401