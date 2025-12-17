from typing import List
from fastapi import Request
from pydantic import TypeAdapter
from starlette.responses import JSONResponse
from app.backend.routers.base import BaseRouter
from app.crud.chat_message import chat_message_crud
from app.schemas.chat_message import ChatMessageSchema, ChatMessageCreate, ChatMessageUpdate


class ChatMessageRouter(BaseRouter):
    def __init__(self) -> None:
        super().__init__(chat_message_crud, "/chat-messages")

    def setup_routes(self) -> None:
        self.router.add_api_route(self.prefix, self.get_paginated, methods=["GET"], status_code=200)
        self.router.add_api_route(f"{self.prefix}/count", self.get_count, methods=["GET"], status_code=200)
        self.router.add_api_route(f"{self.prefix}/{{item_id}}", self.get_by_id, methods=["GET"], status_code=200)
        self.router.add_api_route(self.prefix, self.create_item, methods=["POST"], status_code=201)
        self.router.add_api_route(f"{self.prefix}/{{item_id}}", self.update_item, methods=["PUT"], status_code=200)
        self.router.add_api_route(f"{self.prefix}/{{item_id}}", self.delete_item, methods=["DELETE"], status_code=200)

    async def get_paginated(self, request: Request, page: int = 1, page_size: int = 10) -> list[ChatMessageSchema]:
        items = await super().get_paginated(request, page, page_size)
        return TypeAdapter(List[ChatMessageSchema]).validate_python(items)

    async def get_by_id(self, request: Request, item_id: int) -> ChatMessageSchema:
        return await super().get_by_id(request, item_id)

    async def create_item(self, request: Request, body: ChatMessageCreate) -> ChatMessageSchema:
        return await self.model_crud.create(request.state.session, body)

    async def update_item(self, request: Request, item_id: int, body: ChatMessageUpdate) -> ChatMessageSchema:
        return await self.model_crud.update(request.state.session, item_id, body)

    async def delete_item(self, request: Request, item_id: int):
        item = await self.model_crud.delete(request.state.session, item_id)
        if item is None:
            return JSONResponse(status_code=404, content={"detail": "Item not found"})
        return item


chat_message_router = ChatMessageRouter().router
