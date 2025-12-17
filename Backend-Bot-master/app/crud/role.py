from app.crud.base import CrudBase
from app.models.role import Role
from app.schemas.role import RoleSchema, RoleCreate, RoleUpdate


class RoleCrud(CrudBase[Role, RoleSchema]):
    def __init__(self) -> None:
        super().__init__(Role, RoleSchema)


role_crud = RoleCrud()
