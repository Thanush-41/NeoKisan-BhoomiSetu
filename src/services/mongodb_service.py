"""
MongoDB service for BhoomiSetu chat storage
Handles user chat threads and messages
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
import logging

logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self):
        # Use MongoDB Atlas from environment, fallback to local
        self.connection_string = os.getenv('MONGO_URL', os.getenv('MONGODB_URL', 'mongodb://localhost:27017/'))
        self.database_name = os.getenv('MONGODB_DATABASE', 'bhoomisetu')
        self.client = None
        self.db = None
        self.is_connected = False
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            await self.client.admin.command('ping')
            self.is_connected = True
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.is_connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Disconnected from MongoDB")
    
    async def create_chat_thread(self, user_id: str, title: str, messages: List[Dict] = None) -> str:
        """Create a new chat thread"""
        try:
            if not self.is_connected:
                await self.connect()
                
            thread_data = {
                'user_id': user_id,
                'title': title,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'message_count': len(messages) if messages else 0,
                'last_message': messages[-1]['content'] if messages else None
            }
            
            # Insert thread
            result = await self.db.chat_threads.insert_one(thread_data)
            thread_id = str(result.inserted_id)
            
            # Insert messages if provided
            if messages:
                for message in messages:
                    await self.save_message(thread_id, message['content'], message['is_user'], message.get('timestamp'))
            
            logger.info(f"Created chat thread {thread_id} for user {user_id}")
            return thread_id
            
        except Exception as e:
            logger.error(f"Error creating chat thread: {e}")
            raise
    
    async def save_message(self, thread_id: str, content: str, is_user: bool, timestamp: datetime = None) -> str:
        """Save a message to a chat thread"""
        try:
            if not self.is_connected:
                await self.connect()
                
            message_data = {
                'thread_id': thread_id,
                'content': content,
                'is_user': is_user,
                'timestamp': timestamp or datetime.utcnow()
            }
            
            # Insert message
            result = await self.db.chat_messages.insert_one(message_data)
            
            # Update thread's last message and message count
            await self.db.chat_threads.update_one(
                {'_id': self._to_object_id(thread_id)},
                {
                    '$set': {
                        'last_message': content,
                        'updated_at': datetime.utcnow()
                    },
                    '$inc': {'message_count': 1}
                }
            )
            
            logger.info(f"Saved message to thread {thread_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise
    
    async def get_user_threads(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's chat threads"""
        try:
            if not self.is_connected:
                await self.connect()
                
            cursor = self.db.chat_threads.find(
                {'user_id': user_id}
            ).sort('updated_at', -1).limit(limit)
            
            threads = []
            async for thread in cursor:
                # Convert MongoDB document to frontend-friendly format
                formatted_thread = {
                    'id': str(thread['_id']),
                    'title': thread.get('title', 'Untitled Chat'),
                    'last_message': thread.get('last_message', 'No messages yet'),
                    'message_count': thread.get('message_count', 0),
                    'created_at': thread.get('created_at'),
                    'updated_at': thread.get('updated_at'),
                    'user_id': thread.get('user_id')
                }
                threads.append(formatted_thread)
            
            return threads
            
        except Exception as e:
            logger.error(f"Error getting user threads: {e}")
            return []
    
    async def get_thread_messages(self, thread_id: str, limit: int = 100) -> List[Dict]:
        """Get messages from a chat thread"""
        try:
            if not self.is_connected:
                await self.connect()
                
            cursor = self.db.chat_messages.find(
                {'thread_id': thread_id}
            ).sort('timestamp', 1).limit(limit)
            
            messages = []
            async for message in cursor:
                message['_id'] = str(message['_id'])
                messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting thread messages: {e}")
            return []
    
    async def delete_thread(self, thread_id: str, user_id: str) -> bool:
        """Delete a chat thread and its messages"""
        try:
            if not self.is_connected:
                await self.connect()
                
            # Verify thread belongs to user
            thread = await self.db.chat_threads.find_one({
                '_id': self._to_object_id(thread_id),
                'user_id': user_id
            })
            
            if not thread:
                return False
            
            # Delete messages
            await self.db.chat_messages.delete_many({'thread_id': thread_id})
            
            # Delete thread
            await self.db.chat_threads.delete_one({'_id': self._to_object_id(thread_id)})
            
            logger.info(f"Deleted thread {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting thread: {e}")
            return False
    
    async def update_thread_title(self, thread_id: str, user_id: str, new_title: str) -> bool:
        """Update chat thread title"""
        try:
            if not self.is_connected:
                await self.connect()
                
            result = await self.db.chat_threads.update_one(
                {
                    '_id': self._to_object_id(thread_id),
                    'user_id': user_id
                },
                {
                    '$set': {
                        'title': new_title,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating thread title: {e}")
            return False
    
    def _to_object_id(self, id_string: str):
        """Convert string ID to ObjectId"""
        from bson import ObjectId
        try:
            return ObjectId(id_string)
        except:
            # If conversion fails, return the string (for fallback)
            return id_string
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            if not self.is_connected:
                await self.connect()
                
            total_threads = await self.db.chat_threads.count_documents({})
            total_messages = await self.db.chat_messages.count_documents({})
            
            # Get unique users count
            unique_users = len(await self.db.chat_threads.distinct('user_id'))
            
            return {
                'total_threads': total_threads,
                'total_messages': total_messages,
                'unique_users': unique_users,
                'connection_status': self.is_connected
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'total_threads': 0,
                'total_messages': 0,
                'unique_users': 0,
                'connection_status': False,
                'error': str(e)
            }

# Global instance
mongodb_service = MongoDBService()

# Startup and shutdown handlers
async def startup_mongodb():
    """Initialize MongoDB connection on startup"""
    try:
        await mongodb_service.connect()
    except Exception as e:
        logger.warning(f"MongoDB connection failed, will retry on first use: {e}")

async def shutdown_mongodb():
    """Close MongoDB connection on shutdown"""
    await mongodb_service.disconnect()
