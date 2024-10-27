from typing import Optional

from fastapi_users import schemas
from fastapi_users.schemas import PYDANTIC_V2
from pydantic import ConfigDict, BaseModel
from pydantic import EmailStr


class UserRead(BaseModel):
    id: int
    email: str
    nickname: str
    # role_id: int

    if PYDANTIC_V2:  # pragma: no cover
        model_config = ConfigDict(from_attributes=True)  # type: ignore
    else:  # pragma: no cover

        class Config:
            orm_mode = True


class UserCreate(BaseModel):
    nickname: str
    email: str
    password: str
    # role_id: int


class WalletCreate(BaseModel):
    wallet: str
    wallet_id: int
    crypto: int
