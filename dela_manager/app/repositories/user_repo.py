from sqlalchemy.orm import Session
from app.models import User
from app.schems import UserCreate
import bcrypt

class UserRepository:

    

    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def create(self, user_data: UserCreate):
        
        hashed = bcrypt.hashpw(user_data.password.encode("utf-8"), bcrypt.gensalt())
        new_user = User(
            username=user_data.username,
            hashed_password=hashed.decode("utf-8")
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def verify_password(self, plain_password: str, hashed_password: str):
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))