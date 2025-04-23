import secrets, os, random
from faker import Faker
from typing import Annotated
from datetime import datetime, timedelta, timezone
import jwt
from jwt import PyJWKError
from sqlmodel import Session, select, func
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from passlib.context import CryptContext
from config.config_db import get_session
from models.ultramarines import Ultramarine, TokenData

# Password, permission and token configuration

RANK_HIERARCHY = {
    "legionary": 1,
    "sergeant": 2,
    "lieutenant": 3,
    "captain": 4,
    "legatus": 5,
    "chapter master": 6,
}

SCOPE_PERMISSIONS = {
    "view": 1,
    "update": 3,  # lieutenant and above
    "delete": 5,  # legatus and above
    "re-write": 6,  # chapter master and above
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/ultramarines_chapter/token", scopes={})

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password, hashed_password):
    """Verifies password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hashes plain text password"""
    return pwd_context.hash(password)


def get_user(session: Session, name: str):
    """Returns current user info"""
    statement = select(Ultramarine).where(Ultramarine.name == name)
    user = session.exec(statement).first()
    return user


def get_scopes_for_rank(rank: str) -> list[str]:
    """Returns the allowed scopes for a given rank"""
    rank_level = RANK_HIERARCHY.get(rank.lower(), 0)
    return [scope for scope, required_level in SCOPE_PERMISSIONS.items() if rank_level >= required_level]


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Creates access token for authorization"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# User verification utilities
def authenticate_user(session: Session, name: str, password: str):
    """Authenticate's if user data entered is correct"""
    ultramarine_user = get_user(session, name)
    if not ultramarine_user or not verify_password(password, ultramarine_user.password):
        return False
    return ultramarine_user


async def get_current_ultramarine(
    session: Annotated[Session, Depends(get_session)],
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
):
    """Returns current user and its allowed permissions"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"www-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, name=name)
    except PyJWKError:
        raise credentials_exception
    ultramarine_user = get_user(session, name=token_data.name)
    if name is None:
        raise credentials_exception
    if ultramarine_user is None:
        raise credentials_exception
    user_rank_level = RANK_HIERARCHY.get(ultramarine_user.rank.lower(), 0)
    for scope in security_scopes.scopes:
        required_rank_level = SCOPE_PERMISSIONS.get(scope, 999)  # default to very high if not matched
        if user_rank_level < required_rank_level:
            raise HTTPException(
                status_code=403,
                detail="Not enough permission",
                headers={"www-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'},
            )
    return ultramarine_user


async def get_current_active_ultramarine(current_user: Annotated[Ultramarine, Depends(get_current_ultramarine)]):
    """Returns current active user"""
    if not current_user.status:
        raise HTTPException(status_code=400, detail="Ultramarine de-activated.")
    return current_user


# Function to generate random Ultramarines
async def generate_random_ultramarines(
    session: Annotated[Session, Depends(get_session)],
    num_records=10,
):
    """Generates random ultramarines on startup of app if database is not populated"""
    ranks = ["Legionary", "Sergeant", "Lieutenant", "Captain", "Legatus", "Chapter Master"]
    abilities = ["Superhuman Strength", "Tactical Genius", "Master of War", "Combat Stimulants", "Precise Aim"]
    weapons = ["Bolt Pistol", "Chainsword", "Power Sword", "Plasma Gun", "Heavy Bolter"]

    existing_ultramarines = session.exec(select(func.count()).select_from(Ultramarine)).one()

    if existing_ultramarines > 0:
        print("Ultramarines already exist in the database. Skipping generation.")
        return []  # Return an empty list if Ultramarines already exist

    fake = Faker()

    ultramarines = []
    plain_passwords = {}
    for _ in range(num_records):
        dummy_name = fake.name()
        dummy_password = fake.password()
        plain_passwords[dummy_name] = dummy_password
        ultramarine = Ultramarine(
            name=dummy_name,
            password=get_password_hash(dummy_password),
            primarch="Robute Guilliman",  # Default
            home_world=fake.city(),
            chapter_master=fake.name(),
            codex_complaint=random.choice([True, False]),
            role=random.choice([None, "Warrior", "Commander", "Techmarine", "Apothecary"]),
            rank=random.choice(ranks),
            abilities=random.sample(abilities, random.randint(1, 3)),  # Random abilities
            weapons=random.sample(weapons, random.randint(1, 2)),  # Random weapons
            status=random.choice([True, False]),
        )
        ultramarines.append(ultramarine)

        session.add_all(ultramarines)
        session.commit()
    with open("dummy_data.txt", "w") as file:
        for key, value in plain_passwords.items():
            file.write(f"{key}: {value}\n")

    return ultramarines
