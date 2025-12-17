from app.crud.base import CrudBase
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionSchema


class TransactionCrud(CrudBase[Transaction, TransactionSchema]):
    def __init__(self) -> None:
        super().__init__(Transaction, TransactionSchema)


transaction_crud = TransactionCrud()
