from sqlalchemy.ext.asyncio import AsyncSession

from repositories.base import BaseRepository
from models.user import User


class UsersRepo(BaseRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get(
            self,
            user_id: int
    ) -> User:
        user = await self.get_by(
            "id",
            user_id,
            unique=True
        )
        return user
