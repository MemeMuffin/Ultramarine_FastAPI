from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password="#CaJNHbFr0"):
    """Hashes plain text password"""
    return pwd_context.hash(password)

print(get_password_hash())