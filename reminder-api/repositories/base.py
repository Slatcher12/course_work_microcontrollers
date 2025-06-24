from typing import Any, Generic, Type, TypeVar, Optional, Union
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select
from sqlalchemy import or_

from database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base class for data repositories."""

    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.model_class: Type[ModelType] = model
        self.session: AsyncSession = session
        self.model = model

    async def create(self, attributes: dict[str, Any] = None) -> ModelType:
        if attributes is None:
            attributes = {}
        model = self.model_class(**attributes)
        self.session.add(model)
        return model

    async def get_all(
            self, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        query = self.query()
        query = query.offset(skip).limit(limit)
        return await self.all(query)

    async def get_by(
            self,
            field: str,
            value: Any,
            unique: bool = False,
    ) -> Union[ModelType, list[ModelType]]:
        query = self.query()
        query = await self._get_by(query, field, value)
        if unique:
            return await self.one(query)
        else:
            return await self.all(query)

    async def delete(self, model: ModelType) -> None:
        await self.session.delete(model)

    def query(
            self,
            order_: Optional[dict] = None,
    ) -> Select:
        query = select(self.model_class)
        query = self._maybe_ordered(query, order_)
        return query

    async def all(self, query: Select) -> list[ModelType]:
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def one(self, query: Select) -> ModelType:
        result = await self.session.execute(query)
        return result.scalars().first()

    async def _get_by(self, query: Select, field: str, value: Any) -> Select:
        return query.where(getattr(self.model_class, field) == value)

    def _maybe_ordered(self, query: Select, order_: Optional[dict] = None) -> Select:
        if order_:
            if order_["asc"]:
                for order in order_["asc"]:
                    query = query.order_by(getattr(self.model_class, order).asc())
            else:
                for order in order_["desc"]:
                    query = query.order_by(getattr(self.model_class, order).desc())
        return query

    async def search(self, value: str, *fields: str) -> list[ModelType]:
        """Search entities by substring in given fields."""
        if not fields:
            raise ValueError("At least one field must be provided to search")

        query = self.query()
        search_conditions = [
            getattr(self.model_class, field).ilike(f"%{value}%") for field in fields
        ]
        query = query.where(or_(*search_conditions))

        return await self.all(query)
