"""Models for the ultramarines"""

from sqlmodel import SQLModel, Field, JSON, Column
from pydantic import BaseModel


class Ultramarine(SQLModel, table=True):
    """Base Ultramarines class model"""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    password: str = Field(index=True)
    primarch: str = Field(default="Robute Guilliman", index=True)
    home_world: str | None = Field(default=None, index=True)
    chapter_master: str = Field(index=True)
    codex_complaint: bool = Field(default=False, index=True)
    role: str | None = Field(default=None, index=True)
    rank: str = Field(index=True)
    abilities: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    weapons: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: bool = Field(default="True", index=True)

    # Needed for Column(JSON)
    class Config:
        arbitrary_types_allowed = True


class CreateUltramarine(BaseModel):
    """Creates new ultramarines to server the emperor"""

    name: str
    password: str
    home_world: str
    chapter_master: str
    role: str
    rank: str
    abilities: list[str] | None = None
    weapons: list[str] | None = None
    codex_complaint: bool
    status: bool


class UpdateUltramarine(BaseModel):
    """Updates existing ultramarines information"""

    name: str | None = None
    home_world: str | None = None
    chapter_master: str | None = None
    role: str | None = None
    rank: str | None = None
    abilities: list[str] | None = None
    weapons: list[str] | None = None
    codex_complaint: bool | None = None
    status: bool | None = None


class PublicUltramarine(BaseModel):
    """Display's an ultramarines information"""

    id: int
    name: str
    primarch: str
    home_world: str | None = None
    chapter_master: str
    codex_complaint: bool
    role: str | None = None
    rank: str
    abilities: list[str] | None = None
    weapons: list[str] | None = None
    status: bool

    class Config:
        """Enables ORM for this class"""

        orm_mode = True


class Token(BaseModel):
    """Creates token for authorization"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Data associated with token for authentication and permissions"""

    name: str | None = None
    scopes: list[str] = []
