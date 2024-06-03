import httpx
from fastapi import Depends, FastAPI, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from starlette.responses import JSONResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .models import User, Token, TokenData, OAuth2EmailRequestForm
from .database import SessionLocal, get_user_by_email, add_user, UserInDB

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

auth = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db_session: Session, email: str):
    return db_session.query(UserInDB).filter(UserInDB.email == email).first()


def authenticate_user(db_session: Session, email: str, password: str):
    user = get_user(db_session, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        print(f"JWTError: {e}")
        raise credential_exception
    db = SessionLocal()
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credential_exception
    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if getattr(current_user, "disabled", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@auth.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2EmailRequestForm = Depends()):
    db = SessionLocal()
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)

    user.refresh_token = refresh_token
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "id": user.id,
        "email": user.email
    }


@auth.post("/token/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        db = SessionLocal()
        user = get_user(db, email=email)
        if user is None or user.refresh_token != refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
        db.close()
        return {"access_token": access_token, "token_type": "bearer", "id": user.id}
    except JWTError as e:
        print(f"JWTError: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@auth.post("/register/", response_model=User)
async def register_user(user: User, request: Request):
    db = SessionLocal()
    if get_user_by_email(db, user.email):
        db.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)

    new_user = UserInDB(
        email=user.email,
        hashed_password=hashed_password,
        refresh_token=refresh_token
    )

    try:
        added_user = add_user(db, email=user.email, hashed_password=hashed_password, refresh_token=refresh_token)
        db.commit()

        try:
            # Пытаемся добавить пользователя в backend через Nginx
            await add_user_to_backend(added_user.id, new_user.email, access_token)
        except httpx.HTTPStatusError as e:
            await remove_user_from_auth(db, added_user.id)
            raise HTTPException(status_code=e.response.status_code, detail=f"Failed to add user to backend: {e.response.text}")
        except httpx.RequestError as e:
            await remove_user_from_auth(db, added_user.id)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Connection error to backend: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        db.close()

    response_body = {
        "email": new_user.email,
        "id": added_user.id,
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

    return JSONResponse(content=response_body)


async def add_user_to_backend(user_id: int, email: str, access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://nginx/backend/users",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"id": user_id, "email": email}
        )
        response.raise_for_status()


async def remove_user_from_auth(db: Session, user_id: int):
    user = db.query(UserInDB).filter(UserInDB.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()


@auth.get("/validate")
async def validate_token_endpoint(token: str = Depends(oauth2_scheme)):
    try:
        current_user = await get_current_user(token)
        return {"message": "Token is valid"}
    except HTTPException as e:
        raise e
