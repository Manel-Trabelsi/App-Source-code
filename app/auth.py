from fastapi_login import LoginManager
from .database import SessionLocal
from .crud import get_user_by_username
from passlib.context import CryptContext

SECRET = "super-secret-key"  # CHANGE ME!

manager = LoginManager(SECRET, token_url="/login", use_cookie=True)
manager.cookie_name = "access-token"
manager.cookie_samesite = "lax"
manager.cookie_secure = False

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@manager.user_loader()
def load_user(username: str):
    db = SessionLocal()
    user = get_user_by_username(db, username)
    return user


def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
