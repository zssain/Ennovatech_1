from fastapi import WebSocket
from typing import Dict, List, Set
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        self.department_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, department_id: int):
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        # Add to department connections
        if department_id not in self.department_connections:
            self.department_connections[department_id] = set()
        self.department_connections[department_id].add(websocket)
        
        logger.info(f"User {user_id} connected to WebSocket")

    def disconnect(self, websocket: WebSocket, user_id: int, department_id: int):
        # Remove from user connections
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from department connections
        if department_id in self.department_connections:
            self.department_connections[department_id].discard(websocket)
            if not self.department_connections[department_id]:
                del self.department_connections[department_id]
        
        logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.user_connections:
            message['timestamp'] = datetime.utcnow().isoformat()
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {str(e)}")

    async def broadcast_to_department(self, message: dict, department_id: int):
        if department_id in self.department_connections:
            message['timestamp'] = datetime.utcnow().isoformat()
            for connection in self.department_connections[department_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to department {department_id}: {str(e)}")

    async def broadcast_task_update(self, task_data: dict, department_id: int):
        message = {
            'type': 'task_update',
            'data': task_data
        }
        await self.broadcast_to_department(message, department_id)

    async def broadcast_performance_update(self, performance_data: dict, department_id: int):
        message = {
            'type': 'performance_update',
            'data': performance_data
        }
        await self.broadcast_to_department(message, department_id)

    async def broadcast_notification(self, notification: dict, user_id: int):
        message = {
            'type': 'notification',
            'data': notification
        }
        await self.send_personal_message(message, user_id)

    async def broadcast_skill_update(self, skill_data: dict, department_id: int):
        message = {
            'type': 'skill_update',
            'data': skill_data
        }
        await self.broadcast_to_department(message, department_id)

    async def broadcast_learning_update(self, learning_data: dict, department_id: int):
        message = {
            'type': 'learning_update',
            'data': learning_data
        }
        await self.broadcast_to_department(message, department_id)

# Create a global instance
websocket_manager = WebSocketManager() 