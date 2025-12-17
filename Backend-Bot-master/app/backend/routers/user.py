from fastapi import Request, HTTPException
from urllib.parse import parse_qsl

from app.crud import user_crud
from app.schemas import UserSchemaCreate, UserSchema
from app.backend.routers.base import BaseRouter
from app.schemas.user import BalanceUpdateResponse


class UserRouter(BaseRouter):
    def __init__(self, model_crud, prefix) -> None:
        super().__init__(model_crud, prefix)

    def setup_routes(self) -> None:
        self.router.add_api_route(f"{self.prefix}", self.get_paginated, methods=["GET"], status_code=200)
        self.router.add_api_route(f"{self.prefix}/{{id}}", self.get_by_telegram_id_or_create, methods=["POST"], status_code=200)
        # self.router.add_api_route(f"{self.prefix}/{{id}}", self.delete, methods=["DELETE"], status_code=202, description='Deactivation, to set is_active=true')
        self.router.add_api_route(f"{self.prefix}/{{id}}", self.update, methods=["PUT"], status_code=200)
        self.router.add_api_route(f"{self.prefix}/update_user_balance/{{user_id}}", self.update_user_balance, methods=["PATCH"], status_code=200)

    async def get_paginated(self, request: Request, page: int = 1, page_size: int = 2) -> list[UserSchema]:
        return await super().get_paginated(request, page, page_size)

    async def get_count(self, request: Request) -> int:
        return await super().get_count(request)

    async def get_by_id(self, request: Request, id: int) -> UserSchema:
        return await super().get_by_id(request, id)

    async def get_by_telegram_id_or_create(self, request: Request, id: int, create_obj: UserSchemaCreate) -> UserSchema:
        return await user_crud.get_by_id_or_create(request.state.session, create_obj)

    async def create(self, request: Request, create_obj: UserSchemaCreate) -> UserSchema:
        return await super().create(request, create_obj)

    async def delete(self, request: Request, id: int) -> int:
        return await self.model_crud.delete(request.state.session, id)

    async def update(self, request: Request, id: int, update_obj: UserSchema) -> UserSchema:
        return await super().update(request, id, update_obj)

    async def update_user_balance(self, request: Request, user_id: int) -> BalanceUpdateResponse:
        data = dict(parse_qsl(request.headers.get("Authorization", {}), strict_parsing=True))
        result = await user_crud.update_user_balance(request.state.session, data.get('user_id') or user_id)
        if result is None:
            raise HTTPException(status_code=404, detail="User not found or balance update function not available")
        return result


user_router = UserRouter(user_crud, "/users").router
