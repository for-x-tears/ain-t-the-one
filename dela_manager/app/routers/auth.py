from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schems import UserCreate, UserResponse
from app.repositories.user_repo import UserRepository
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "quiet_secret_key"
ALGORITHM = "HS256"

def create_access_token(user_id: str):
    data = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=60)
    }
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    existing_user = repo.get_by_username(user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = repo.create(user_data)
    return new_user

@router.post("/login")
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_by_username(user_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    password_ok = repo.verify_password(user_data.password, user.hashed_password)
    if not password_ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}