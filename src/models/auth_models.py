"""
Pydantic models for authentication and user management
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserRegistration(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class TokenVerification(BaseModel):
    token: str

class UserResponse(BaseModel):
    uid: str
    email: str
    display_name: Optional[str] = None
    token: str

class ChatThreadCreate(BaseModel):
    title: Optional[str] = None

class ChatMessage(BaseModel):
    thread_id: str
    message: str
    location: Optional[str] = None

class ChatThreadResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message: Optional[str] = None

class ChatMessageResponse(BaseModel):
    id: str
    thread_id: str
    user_message: str
    ai_response: str
    location: Optional[str] = None
    timestamp: datetime
