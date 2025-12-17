from app.crud.base import CrudBase
from app.models.chat_message import ChatMessage
from app.schemas.chat_message import ChatMessageSchema


class ChatMessageCrud(CrudBase[ChatMessage, ChatMessageSchema]):
    def __init__(self) -> None:
        super().__init__(ChatMessage, ChatMessageSchema)


chat_message_crud = ChatMessageCrud()
