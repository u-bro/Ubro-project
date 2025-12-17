from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import update, insert, select, text
from sqlalchemy.exc import SQLAlchemyError
from app.crud.base import CrudBase
from app.models import User
from app.schemas import UserSchema, UserSchemaCreate
from app.logger import logger
from app.schemas.user import BalanceUpdateResponse


class CrudUser(CrudBase):
    async def update_user_balance(self, session: AsyncSession, user_id: int) -> BalanceUpdateResponse | None:
        stmt = text("SELECT update_user_balance(:user_id)").params(user_id=user_id)
        
        try: 
            result = await self.execute_get_one(session, stmt)
        except SQLAlchemyError as e:
            logger.exception("DB error in update_user_balance")
            raise
        
        if result is None:
            return None
        # result is a Row or scalar - convert to dict for validation
        if hasattr(result, '_mapping'):
            return BalanceUpdateResponse.model_validate(dict(result._mapping))
        elif isinstance(result, dict):
            return BalanceUpdateResponse.model_validate(result)
        else:
            # If it's a single value from the function, wrap it
            return BalanceUpdateResponse(success=bool(result))

    

    async def get_by_telegram_id(self, session: AsyncSession, telegram_id: int) -> UserSchema:
        result = await session.execute(select(self.model).where(self.model.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        return self.schema.model_validate(user) if user else None

    async def update_inviter_id(self, session: AsyncSession, telegram_id: int, inviter_id: int) -> UserSchema:
        stmt = (
            update(self.model)
            .where(self.model.telegram_id == telegram_id)
            .values({'inviter_id': inviter_id})
            .returning(self.model)
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return self.schema.model_validate(user) if user else None

    async def get_by_id_or_create(self, session: AsyncSession, user_object: UserSchemaCreate) -> UserSchema | None:
        try:
            stmt = select(self.model).where(self.model.telegram_id == user_object.telegram_id)
            result = await session.execute(stmt)
            existing_user = result.scalars().first()

            if existing_user:
                return self.schema.model_validate(existing_user)

            stmt = insert(self.model).values(user_object.model_dump()).returning(self.model)
            result = await session.execute(stmt)
            created_user = result.scalars().first()
            return self.schema.model_validate(created_user) if created_user else None

        except exc.IntegrityError:
            await session.rollback()
            try:
                stmt = select(self.model).where(self.model.telegram_id == user_object.telegram_id)
                result = await session.execute(stmt)
                existing_user = result.scalars().first()
                return self.schema.model_validate(existing_user) if existing_user else None
            except exc.NoResultFound:
                return None

        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating user: {e}")
            return None

    async def delete(self, session: AsyncSession, id: int) -> UserSchema | None:
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(is_active=False)
            .returning(self.model)
        )
        result = await self.execute_get_one(session, stmt)
        return self.schema.model_validate(result) if result else None


user_crud: CrudUser = CrudUser(User, UserSchema)