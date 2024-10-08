import jwt
import datetime
from flask import current_app, request, jsonify, Response
from app.models import Users
from functools import wraps
from typing import Callable, Union, Any

FuncType = Callable[..., Any]

def encode_auth_token(user_id: int) -> Union[str, Exception]:
    try:
        payload = {
            "exp": datetime.datetime.now() + datetime.timedelta(days=1),
            "iat": datetime.datetime.now(),
            "sub": user_id
        }
        return jwt.encode(payload, current_app.config.get("SECRET_KEY"), algorithm="HS256")
    except Exception as e:
        return e

def decode_auth_token(auth_token: str) -> Union[int, str]:
    try:
        payload = jwt.decode(auth_token, current_app.config.get("SECRET_KEY"), algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        return "Signature expired. Please log in again."
    except jwt.InvalidTokenError:
        return "Invalid token. Please log in again"

def token_required(func: FuncType) -> FuncType:
    @wraps(func)
    def decorated(*args: Any, **kwargs: Any) -> Response:
        token = None
        if "Authorization" in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.split()[1] if len(bearer.split()) > 1 else None
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        user_id = decode_auth_token(token)
        if isinstance(user_id, str):
            return jsonify({'message': user_id}), 401
        current_user = Users.query.get(user_id)
        if not current_user:
            return jsonify({'message': 'User not found!'}), 401
        return func(current_user, *args, **kwargs)
    return decorated


def permission_collector(func: FuncType) -> FuncType:
    @wraps(func)
    def decorated_function(current_user: Users, *args: Any, **kwargs: Any) -> Response:
        user_permissions = set()
        user_permissions.update([perm.name for perm in current_user.permissions])
        for group in current_user.groups:
            user_permissions.update([perm.name for perm in group.permissions])
        return func(current_user, user_permissions, *args, **kwargs)
    return decorated_function