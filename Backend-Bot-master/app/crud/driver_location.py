from app.crud.base import CrudBase
from app.models.driver_location import DriverLocation
from app.schemas.driver_location import DriverLocationSchema


class DriverLocationCrud(CrudBase[DriverLocation, DriverLocationSchema]):
    def __init__(self) -> None:
        super().__init__(DriverLocation, DriverLocationSchema)


driver_location_crud = DriverLocationCrud()
