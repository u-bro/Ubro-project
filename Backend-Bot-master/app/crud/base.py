from typing import Any, Dict, List, Optional, TypeVar, Generic

from sqlalchemy import UniqueConstraint, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import insert, delete, func, update
from sqlalchemy.future import select
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.expression import and_, or_
from app.logger import logger
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import text, column


M = TypeVar('M')
S = TypeVar('S')


class CrudBase(Generic[M, S]):
    def __init__(self, model: M, schema: S):
        self.model = model
        self.schema = schema

    async def execute_get_one(self, session: AsyncSession, stmt) -> M:
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_paginated(self, session: AsyncSession, page: int = 1, page_size: int = 2) -> list[S]:
        offset = (page - 1) * page_size
        result = await session.execute(select(self.model).offset(offset).limit(page_size))
        gpus = result.scalars().all()
        return [self.schema.model_validate(gpu) for gpu in gpus]

    async def get_count(self, session: AsyncSession) -> int:
        result = await session.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()

    async def get_by_id(self, session: AsyncSession, id: int) -> S | None:
        result = await session.execute(select(self.model).where(self.model.id == id))
        gpu = result.scalar_one_or_none()
        return self.schema.model_validate(gpu) if gpu else None

    async def create(self, session: AsyncSession, create_obj: S) -> S | None:
        stmt = insert(self.model).values(create_obj.model_dump()).returning(self.model)
        result = await self.execute_get_one(session, stmt)
        return self.schema.model_validate(result) if result else None

    async def delete(self, session: AsyncSession, id: int) -> S | None:
        stmt = delete(self.model).where(self.model.id == id).returning(self.model)
        result = await self.execute_get_one(session, stmt)
        
        return self.schema.model_validate(result) if result else None

    async def update(self, session: AsyncSession, id: int, update_obj: S) -> S | None:
        update_data = update_obj.model_dump(exclude_none=True)
        
        # If no fields to update, just return the existing record
        if not update_data:
            return await self.get_by_id(session, id)
        
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(update_data)
            .returning(self.model)
        )
        result = await self.execute_get_one(session, stmt)
        return self.schema.model_validate(result) if result else None

    async def batch_create(self, session: AsyncSession, create_objs: list[S]):
        create_dicts = [obj.model_dump() for obj in create_objs]
        stmt = insert(self.model).values(create_dicts).returning(True)
        result = await session.execute(stmt)
        return result.scalars().all() if result else None

    async def batch_delete(self, session: AsyncSession, ids: list[int]):
        stmt = delete(self.model).where(self.model.id.in_(ids)).returning(True)
        result = await session.execute(stmt)
        return result.scalars().all() if result else None
    
    async def batch_upsert(
        self,
        session: AsyncSession, 
        create_objs: list[S],
        *,
        not_update: list[str] = None,
        on_conflict: list[str] = None,
        log: bool = False
    ) -> list[dict]:
        """
        Универсальный UPSERT для обновления/вставки записей.

        Args:
            not_update: Поля, по которым идентифицируем запись (если None, используется primary key)
            log: Вывод вставки
        """
        if not create_objs:
            return []

        create_dicts = [obj.model_dump() for obj in create_objs]

        # Определяем поля для идентификации записей
        if not_update is None:
            mapper = inspect(self.model)
            not_update = [col.key for col in mapper.primary_key]

        stmt = pg_insert(self.model).values(create_dicts)

        # Определяем поля для обновления (все, кроме идентификационных)
        update_fields = {
            col: getattr(stmt.excluded, col)
            for col in create_dicts[0].keys()
            if col not in not_update
        }

        if not update_fields:
            return []

        try:
            stmt = stmt.on_conflict_do_update(
                index_elements=on_conflict,
                set_=update_fields
            ).returning(self.model)  

            result = await session.execute(stmt)
            updated_records = result.scalars().all()

            if log:
                updated_columns = list(update_fields.keys())
                logger.info(
                    f"Upserted {len(updated_records)} records in {self.model.__tablename__}. Updated columns: {', '.join(updated_columns)}"
                )

            return [
                {
                    column.key: getattr(record, column.key)
                    for column in inspect(self.model).mapper.column_attrs
                }
                for record in updated_records
            ]

        except Exception as e:
            logger.error(f"Error during upsert: {str(e)}")
            raise


    async def get_paginated_with_filters(
             self,
             session: AsyncSession,
             page: int = 1,
             page_size: int = 10,
             filters: Optional[Dict[str, Any]] = None,
             sort_by: Optional[str] = None,
             sort_desc: bool = False
         ) -> List[S]:
        offset = (page - 1) * page_size
        stmt = select(self.model).offset(offset).limit(page_size)
        
        if filters:
            conditions = self._apply_filters(filters)
            if conditions:
                stmt = stmt.where(and_(*conditions))
        
        if sort_by and hasattr(self.model, sort_by):
            order_by = getattr(self.model, sort_by)
            stmt = stmt.order_by(order_by.desc() if sort_desc else order_by.asc())
        
        result = await session.execute(stmt)
        items = result.scalars().all()
        return [self.schema.model_validate(item) for item in items]

    def _apply_filters(self, filters: Dict[str, Any]):
        conditions = []
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                column: InstrumentedAttribute = getattr(self.model, field)
                
                if isinstance(value, dict):
                    if "from" in value and value["from"] is not None:
                        conditions.append(column >= value["from"])
                    if "to" in value and value["to"] is not None:
                        conditions.append(column <= value["to"])
                
                elif isinstance(value, list):
                    if value:
                        conditions.append(column.in_(value))
                
                else:
                    conditions.append(column == value)
                    
        return conditions
    
    # # EXAMPLE:
    #
    # filters = {
    # # Range filtering
    # "price": {"from": 500, "to": 1500},  # price BETWEEN 500 AND 1500
    # "income": {"from": 20.5},            # income >= 20.5
    #
    # # Exact match filtering
    # "name": "RTX 3090",   
    # "manufacturer": "NVIDIA",  
    #
    # # Boolean filtering (supports both True/False and 1/0)
    # "is_crafted": True,  # is_crafted = TRUE
    # "is_available": 1,   # is_available = 1 (same as True)
    # 
    # # List filtering (IN condition)
    # "rarity": [1, 2, 3],        # rarity IN (1, 2, 3)
    # "status": ["new", "used"],  # status IN ('new', 'used')
    #
    # # And their combinations
