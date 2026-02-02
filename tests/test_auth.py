import pytest
from app.core.security import create_access_token, verify_password, get_password_hash
from jose import jwt
from app.core.config import settings

def test_password_hashing():
    password = "secret_test_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)

def test_jwt_token_creation():
    user_id = "test_user_id"
    token = create_access_token(subject=user_id)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == user_id
    assert "exp" in payload
