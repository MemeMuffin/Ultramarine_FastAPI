from typing import Annotated
from datetime import timedelta
from fastapi import Depends, Security, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from config.config_db import get_session
from models.ultramarines import Token, PublicUltramarine, CreateUltramarine, UpdateUltramarine, Ultramarine
from routes.utils import (
    get_user,
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_scopes_for_rank,
    get_password_hash,
    get_current_active_ultramarine,
)

ultramarine_routes = APIRouter()


@ultramarine_routes.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]
):
    """Generates JWT token for user authorization"""
    ultramarine_user = authenticate_user(session, form_data.username, form_data.password)
    if not ultramarine_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect name or password",
            headers={"www-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    scopes = get_scopes_for_rank(ultramarine_user.rank)
    access_token = create_access_token(
        data={"sub": ultramarine_user.name, "scopes": scopes}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="Bearer")


@ultramarine_routes.post("/register/", response_model=PublicUltramarine)
async def register_ultramarine(ultramarine_user: CreateUltramarine, session: Annotated[Session, Depends(get_session)]):
    """Recurits new ultramarines for the emepror's mission"""
    db_ultramarine = get_user(session, name=ultramarine_user.name)
    if db_ultramarine:
        raise HTTPException(status_code=400, detail="Ultramarine already recurited")
    hashed_password = get_password_hash(ultramarine_user.password)
    new_ultramarine = Ultramarine(
        name=ultramarine_user.name,
        password=hashed_password,
        home_world=ultramarine_user.home_world,
        chapter_master=ultramarine_user.chapter_master,
        role=ultramarine_user.role,
        rank=ultramarine_user.rank,
        abilities=ultramarine_user.abilities,
        weapons=ultramarine_user.weapons,
        codex_complaint=ultramarine_user.codex_complaint,
        status=ultramarine_user.status,
    )
    session.add(new_ultramarine)
    session.commit()
    session.refresh(new_ultramarine)
    return new_ultramarine


@ultramarine_routes.get("/active/", response_model=PublicUltramarine)
async def read_ultramarines(
    current_ultramarine: Annotated[Ultramarine, Depends(get_current_active_ultramarine)],
):
    """Returns curret active authenticated user"""
    return current_ultramarine


@ultramarine_routes.get(
    "/all/",
    response_model=list[PublicUltramarine],
    dependencies=[Security(get_current_active_ultramarine, scopes=["view"])],
)
async def get_all_ultramarines(
    session: Annotated[Session, Depends(get_session)],
    current_ultramarine: Annotated[Ultramarine, Depends(get_current_active_ultramarine)],
):
    """Gets information on all ultramarines"""
    stmt = select(Ultramarine)
    ultramarines = session.exec(stmt).all()
    return ultramarines


@ultramarine_routes.patch(
    "/update/",
    response_model=PublicUltramarine,
    dependencies=[Security(get_current_active_ultramarine, scopes=["update"])],
)
async def update_ultramarine(
    ultramarine: UpdateUltramarine,
    ultramarine_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_ultramarine: Annotated[Ultramarine, Depends(get_current_active_ultramarine)],
):
    """Updates ultramarine"""
    db_ultramarine = session.get(Ultramarine, ultramarine_id)
    if not db_ultramarine:
        raise HTTPException(status_code=404, detail="Ultramarine not found.")
    for key, value in ultramarine.model_dump(exclude_unset=True).items():
        setattr(db_ultramarine, key, value)

    session.add(db_ultramarine)
    session.commit()
    session.refresh(db_ultramarine)
    return db_ultramarine


@ultramarine_routes.put(
    "/rewrite/",
    response_model=PublicUltramarine,
    dependencies=[Security(get_current_active_ultramarine, scopes=["re-write"])],
)
async def re_write_ultramarine(
    ultramarine_id: int,
    ultramarine: UpdateUltramarine,
    session: Annotated[Session, Depends(get_session)],
    current_ultramarine: Annotated[Ultramarine, Depends(get_current_active_ultramarine)],
):
    """Re-writes an ultramarine"""
    db_ultramarine = session.get(Ultramarine, ultramarine_id)
    if not db_ultramarine:
        raise HTTPException(status_code=404, detail="Ultramarine not found.")
    for key, value in ultramarine.model_dump(exclude_unset=True).items():
        setattr(db_ultramarine, key, value)

    session.add(db_ultramarine)
    session.commit()
    session.refresh(db_ultramarine)
    return db_ultramarine


@ultramarine_routes.delete(
    "/delete/",
    response_model=PublicUltramarine,
    dependencies=[Security(get_current_active_ultramarine, scopes=["delete"])],
)
async def delete_ultramarine(
    ultramarine_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_ultramarine: Annotated[Ultramarine, get_current_active_ultramarine],
):
    """Deletes an ultramarine from the chapter"""
    db_ultramarine = session.get(Ultramarine, ultramarine_id)
    if not db_ultramarine:
        raise HTTPException(status_code=404, detail="Ultramarine not found.")
    session.delete(db_ultramarine)
    session.commit()
    return db_ultramarine, {"codex": "Ultramarine relieved of chapter duties."}
