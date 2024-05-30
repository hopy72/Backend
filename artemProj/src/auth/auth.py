from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from starlette.responses import JSONResponse
from passlib.context import CryptContext
from .models import User, Token, TokenData, OAuth2EmailRequestForm
from .database import SessionLocal, get_user_by_email, add_user, UserInDB, engine

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


def get_user(db_session, email: str):
    return db_session.query(UserInDB).filter(UserInDB.email == email).first()


def authenticate_user(email: str, password: str):
    user = get_user(SessionLocal(), email)
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
        expire = datetime.utcnow() + timedelta(minutes=15)
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
    user = get_user(SessionLocal(), email=token_data.email)
    if user is None:
        raise credential_exception
    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if getattr(current_user, "disabled", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@auth.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2EmailRequestForm = Depends()):
    user = authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires)
    return {"access_token": access_token, "token_type": "bearer",
            "refresh_token": refresh_token, "id": user.id, "email": user.email}


@auth.post("/token/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid refresh token")
        user = get_user(SessionLocal(), email=email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User not found")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer", "id": user.id}
    except JWTError as e:
        print(f"JWTError: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid refresh token")


@auth.post("/register/", response_model=User)
async def register_user(user: User):
    db = SessionLocal()
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)

    new_user = UserInDB(
        email=user.email,
        hashed_password=hashed_password,
        access_token=access_token,
        refresh_token=refresh_token
    )

    added_user = add_user(
        db,
        email=user.email,
        hashed_password=hashed_password,
        access_token=access_token,
        refresh_token=refresh_token
    )

    response_body = {
        "user": {
            "email": new_user.email,
            "id": added_user.id,
        },
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

    return JSONResponse(content=response_body)


@auth.get("/validate")
async def validate_token_endpoint(token: str = Depends(oauth2_scheme)):
    try:
        current_user = await get_current_user(token)
        return {"message": "Token is valid"}
    except HTTPException as e:
        raise e
