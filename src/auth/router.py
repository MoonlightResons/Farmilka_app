from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from sqlalchemy.orm import Session

from .schemas import UserRead, UserCreate, WalletCreate
from .security import get_password_hash, verify_password, create_access_token, create_refresh_token
from database import get_async_session, User, Wallet
from .utilst import generate_code

from config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ALGORITHM


router = APIRouter(
    prefix='/auth',
)


@router.post('/register/', response_model=UserRead, tags=['auth'])
async def register(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    existing_email = await session.execute(select(User).where(User.email == user.email))
    if existing_email.scalar():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already taken')

    # Создание пользователя
    new_user = User(nickname=user.nickname, email=user.email)
    new_user.password = get_password_hash(user.password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # new_user_id = new_user.id

    # # Создание кошелька после регистрации пользователя
    # wallet_data = WalletCreate(
    #     wallet=generate_code(),  # установите значения по умолчанию или генерируемые значения
    #     wallet_id=new_user_id,  # предполагается, что эта функция генерирует уникальный ID
    #     crypto=0  # Начальное количество криптовалюты, например, 0
    # )
    # new_wallet = Wallet(**wallet_data.dict(), user_id=new_user.id)
    # session.add(new_wallet)
    # await session.commit()
    # await session.refresh(new_wallet)

    return new_user


from fastapi.responses import JSONResponse


@router.post('/login/', tags=['auth'])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session)):
    user = await session.execute(select(User).where(User.email == form_data.username))
    user = user.scalar()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response = JSONResponse(content={"message": "Login successful"})

    # Устанавливаем токены как cookie
    response.set_cookie(
        key="access_token", value=access_token, httponly=True, secure=True, samesite="Strict"
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="Strict"
    )

    return response


@router.post('/refresh/', tags=['auth'])
async def refresh_token(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token type")

        user_id = int(payload.get("sub"))
        new_access_token = create_access_token(user_id)

        response = JSONResponse(content={"message": "Token refreshed"})
        response.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=True, samesite="Strict")

        return response
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


