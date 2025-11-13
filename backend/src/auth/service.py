from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from src.core.config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain, hashed):
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def hash_password(password):
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data, expires_delta=None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token):
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
