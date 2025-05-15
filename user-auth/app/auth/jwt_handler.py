from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config.config import SECRET_KEY, ALGORITHM

def create_access_token(data: dict, expires_delta: timedelta, claims: dict = {}):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    # Add custom claims to the refresh token as well
    to_encode.update(claims)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta, claims: dict = {}):
    expire = datetime.utcnow() + expires_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    # Add custom claims to the refresh token as well
    to_encode.update(claims)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(e)
        return None
