from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.schems import UserCreate
import bcrypt

class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str):
        result = await self.db.execute(
            select(User).filter(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate):
        hashed = bcrypt.hashpw(user_data.password.encode("utf-8"), bcrypt.gensalt())
        new_user = User(
            username=user_data.username,
            hashed_password=hashed.decode("utf-8")
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    def verify_password(self, plain_password: str, hashed_password: str):
        # verify синхронная — так и оставляем
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))