from app.crud.base import CrudBase
from app.models.commission import Commission
from app.schemas.commission import CommissionSchema


class CommissionCrud(CrudBase[Commission, CommissionSchema]):
    def __init__(self) -> None:
        super().__init__(Commission, CommissionSchema)


commission_crud = CommissionCrud()
