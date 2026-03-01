from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.database import users_collection
import os
from dotenv import load_dotenv

load_dotenv()

# ========================
# JWT Configuration
# ========================
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ========================
# Password Hashing (FIXED)
# ========================
pwd_context = CryptContext(
    schemes=["bcrypt"],   # ✅ FIXED (was bcrypt_sha256)
    deprecated="auto"
)


# ========================
# OAuth2 Dependency
# ========================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  
# NOTE: no leading slash recommended


# ========================
# Password Utilities
# ========================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ========================
# JWT Utilities
# ========================
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({
        "exp": expire,
        "sub": data.get("sub")   # ✅ ensure username stored
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ========================
# Authentication Logic
# ========================
async def authenticate_user(username: str, password: str):
    user = await users_collection.find_one({"username": username})

    if not user:
        return False

    if not verify_password(password, user["hashed_password"]):
        return False

    return user


# ========================
# Current User Dependency
# ========================
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = await users_collection.find_one({"username": username})

    if user is None:
        raise credentials_exception

    return user


# ========================
# Admin Protection
# ========================
async def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user


async def get_current_admin_user(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user


# ========================
# Bootstrap Admin User
# ========================
async def ensure_admin():
    existing_admin = await users_collection.find_one({"username": "admin"})

    if not existing_admin:
        await users_collection.insert_one({
            "username": "admin",
            "hashed_password": hash_password("admin123"),
            "role": "admin"
        })

        print("✅ Admin created → admin / admin123")