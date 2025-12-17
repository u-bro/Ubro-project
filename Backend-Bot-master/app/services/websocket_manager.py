"""
WebSocket Connection Manager
Управление WebSocket соединениями для real-time коммуникации
"""

from typing import Dict, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Менеджер WebSocket соединений.
    Поддерживает:
    - Множественные соединения для одного пользователя (разные устройства)
    - Отправка сообщений конкретному пользователю
    - Broadcast всем подключённым пользователям
    - Отправка по группам (например, участникам поездки)
    """
    
    def __init__(self):
        # user_id -> list of WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # ride_id -> list of user_ids (для группировки по поездкам)
        self.ride_participants: Dict[int, set] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        """Подключение нового WebSocket клиента"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected: user_id={user_id}, total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: int) -> None:
        """Отключение WebSocket клиента"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Удаляем пользователя если нет активных соединений
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"WebSocket disconnected: user_id={user_id}")
    
    def is_connected(self, user_id: int) -> bool:
        """Проверка подключён ли пользователь"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    async def send_personal_message(self, user_id: int, message: dict) -> bool:
        """
        Отправка сообщения конкретному пользователю.
        Отправляет на все его устройства.
        """
        if user_id not in self.active_connections:
            logger.warning(f"User {user_id} is not connected")
            return False
        
        message_with_timestamp = {
            **message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected = []
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message_with_timestamp)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                disconnected.append(websocket)
        
        # Очистка отключённых соединений
        for ws in disconnected:
            self.active_connections[user_id].remove(ws)
        
        return True
    
    async def broadcast(self, message: dict, exclude_user_id: Optional[int] = None) -> None:
        """Отправка сообщения всем подключённым пользователям"""
        message_with_timestamp = {
            **message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for user_id, connections in self.active_connections.items():
            if exclude_user_id and user_id == exclude_user_id:
                continue
            
            for websocket in connections:
                try:
                    await websocket.send_json(message_with_timestamp)
                except Exception as e:
                    logger.error(f"Broadcast failed for user {user_id}: {e}")
    
    # === Методы для работы с поездками ===
    
    def join_ride(self, ride_id: int, user_id: int) -> None:
        """Присоединение пользователя к комнате поездки"""
        if ride_id not in self.ride_participants:
            self.ride_participants[ride_id] = set()
        self.ride_participants[ride_id].add(user_id)
        logger.info(f"User {user_id} joined ride {ride_id}")
    
    def leave_ride(self, ride_id: int, user_id: int) -> None:
        """Выход пользователя из комнаты поездки"""
        if ride_id in self.ride_participants:
            self.ride_participants[ride_id].discard(user_id)
            if not self.ride_participants[ride_id]:
                del self.ride_participants[ride_id]
        logger.info(f"User {user_id} left ride {ride_id}")
    
    async def send_to_ride(self, ride_id: int, message: dict, exclude_user_id: Optional[int] = None) -> None:
        """Отправка сообщения всем участникам поездки"""
        if ride_id not in self.ride_participants:
            logger.warning(f"No participants in ride {ride_id}")
            return
        
        for user_id in self.ride_participants[ride_id]:
            if exclude_user_id and user_id == exclude_user_id:
                continue
            await self.send_personal_message(user_id, message)
    
    def get_online_users(self) -> List[int]:
        """Получение списка онлайн пользователей"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Общее количество активных соединений"""
        return sum(len(conns) for conns in self.active_connections.values())


# Глобальный экземпляр менеджера
manager = ConnectionManager()
