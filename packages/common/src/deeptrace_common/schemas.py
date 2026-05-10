from typing import Generic, TypeVar, Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

T = TypeVar("T")


class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    roles: List[str] = []
    active: bool = True


class JWTToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class Pagination(BaseModel):
    page: int = 1
    size: int = 10
    total: int = 0
    total_pages: int = 0

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class Success(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None


class Error(BaseModel):
    success: bool = False
    error: str
    code: Optional[str] = None
    details: Optional[dict] = None