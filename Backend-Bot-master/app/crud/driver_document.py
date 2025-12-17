from app.crud.base import CrudBase
from app.models.driver_document import DriverDocument
from app.schemas.driver_document import DriverDocumentSchema


class DriverDocumentCrud(CrudBase[DriverDocument, DriverDocumentSchema]):
    def __init__(self) -> None:
        super().__init__(DriverDocument, DriverDocumentSchema)


driver_document_crud = DriverDocumentCrud()
