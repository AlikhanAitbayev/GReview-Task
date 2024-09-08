import jwt
import datetime
from flask import current_app
from app.models import User

def encode_auth_token(user_id):
    try:
        payload = {
            "exp": datetime.datetime.now() + datetime.timedelta(days=1),
            "iat": datetime.datetime.now(),
            "sub": user_id
        }
        return jwt.encode(payload, current_app.config.get("SECRET_KEY"), algorithm="HS256")
    except Exception as e:
        return e

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, current_app.config.get("SECRET_KEY"), algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        return "Signature expired. Please log in again."
    except jwt.InvalidTokenError:
        return "Invalid token. Please log in again"