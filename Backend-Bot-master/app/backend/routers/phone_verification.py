from typing import List
from fastapi import Request
from pydantic import TypeAdapter
from starlette.responses import JSONResponse
from app.backend.routers.base import BaseRouter
from app.crud.phone_verification import phone_verification_crud
from app.schemas.phone_verification import PhoneVerificationSchema, PhoneVerificationCreate, PhoneVerificationUpdate


class PhoneVerificationRouter(BaseRouter):
    def __init__(self) -> None:
        super().__init__(phone_verification_crud, "/phone-verifications")

    def setup_routes(self) -> None:
        self.router.add_api_route(self.prefix, self.get_paginated, methods=["GET"], status_code=200)
        self.router.add_api_route(f"{self.prefix}/count", self.get_count, methods=["GET"], status_code=200)
        self.router.add_api_route(f"{self.prefix}/{{item_id}}", self.get_by_id, methods=["GET"], status_code=200)
        self.router.add_api_route(self.prefix, self.create_item, methods=["POST"], status_code=201)
        self.router.add_api_route(f"{self.prefix}/{{item_id}}", self.update_item, methods=["PUT"], status_code=200)
        self.router.add_api_route(f"{self.prefix}/{{item_id}}", self.delete_item, methods=["DELETE"], status_code=200)

    async def get_paginated(self, request: Request, page: int = 1, page_size: int = 10) -> list[PhoneVerificationSchema]:
        items = await super().get_paginated(request, page, page_size)
        return TypeAdapter(List[PhoneVerificationSchema]).validate_python(items)

    async def get_by_id(self, request: Request, item_id: int) -> PhoneVerificationSchema:
        return await super().get_by_id(request, item_id)

    async def create_item(self, request: Request, body: PhoneVerificationCreate) -> PhoneVerificationSchema:
        return await self.model_crud.create(request.state.session, body)

    async def update_item(self, request: Request, item_id: int, body: PhoneVerificationUpdate) -> PhoneVerificationSchema:
        return await self.model_crud.update(request.state.session, item_id, body)

    async def delete_item(self, request: Request, item_id: int):
        item = await self.model_crud.delete(request.state.session, item_id)
        if item is None:
            return JSONResponse(status_code=404, content={"detail": "Item not found"})
        return item


phone_verification_router = PhoneVerificationRouter().router
