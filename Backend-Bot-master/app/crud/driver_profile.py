from app.crud.base import CrudBase
from app.models.driver_profile import DriverProfile
from app.schemas.driver_profile import DriverProfileSchema


class DriverProfileCrud(CrudBase[DriverProfile, DriverProfileSchema]):
    def __init__(self) -> None:
        super().__init__(DriverProfile, DriverProfileSchema)


driver_profile_crud = DriverProfileCrud()
