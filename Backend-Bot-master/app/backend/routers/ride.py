from typing import Optional, List
from fastapi import Request, Query, HTTPException
from pydantic import TypeAdapter
from app.backend.routers.base import BaseRouter
from app.crud.ride import ride_crud
from app.schemas.ride import RideSchema, RideCreate, RideUpdate, RideStatusChangeRequest


class RideRouter(BaseRouter):
    def __init__(self) -> None:
        super().__init__(ride_crud, "/rides")

    def setup_routes(self) -> None:
        self.router.add_api_route(self.prefix, self.get_paginated, methods=["GET"], status_code=200)
        self.router.add_api_route(f"{self.prefix}/count", self.get_count, methods=["GET"], status_code=200)
        self.router.add_api_route(f"{self.prefix}/{{ride_id}}", self.get_by_id, methods=["GET"], status_code=200)
        self.router.add_api_route(self.prefix, self.create_ride, methods=["POST"], status_code=201)
        self.router.add_api_route(f"{self.prefix}/{{ride_id}}", self.update_ride, methods=["PUT"], status_code=200)
        self.router.add_api_route(f"{self.prefix}/{{ride_id}}/status", self.change_status, methods=["POST"], status_code=200)

    async def get_paginated(self, request: Request, page: int = 1, page_size: int = 10) -> list[RideSchema]:
        items = await super().get_paginated(request, page, page_size)
        return TypeAdapter(List[RideSchema]).validate_python(items)

    async def get_by_id(self, request: Request, ride_id: int) -> RideSchema:
        return await super().get_by_id(request, ride_id)

    async def create_ride(self, request: Request, body: RideCreate) -> RideSchema:
        return await self.model_crud.create(request.state.session, body)

    async def update_ride(self, request: Request, ride_id: int, body: RideUpdate) -> RideSchema:
        return await self.model_crud.update(request.state.session, ride_id, body)

    async def change_status(self, request: Request, ride_id: int, body: RideStatusChangeRequest) -> RideSchema:
        result = await self.model_crud.change_status(request.state.session, ride_id, body)
        if result is None:
            raise HTTPException(status_code=404, detail="Ride not found or status transition not allowed")
        return result


ride_router = RideRouter().router
