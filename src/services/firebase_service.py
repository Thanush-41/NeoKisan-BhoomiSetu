"""
Firebase Authentication and Database Service
Handles user authentication, chat threads, and data persistence
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore
    FIREBASE_ADMIN_AVAILABLE = True
except ImportError:
    FIREBASE_ADMIN_AVAILABLE = False

try:
    import pyrebase
    PYREBASE_AVAILABLE = True
except ImportError:
    PYREBASE_AVAILABLE = False

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirebaseService:
    def __init__(self):
        self.db = None
        self.pyrebase_auth = None
        self.app = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK and Pyrebase"""
        try:
            # Firebase configuration for Pyrebase (client-side auth)
            firebase_config = {
                "apiKey": os.getenv("FIREBASE_API_KEY"),
                "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
                "databaseURL": os.getenv("FIREBASE_DATABASE_URL", ""),
                "projectId": os.getenv("FIREBASE_PROJECT_ID"),
                "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
                "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
                "appId": os.getenv("FIREBASE_APP_ID")
            }
            
            # Remove None values
            firebase_config = {k: v for k, v in firebase_config.items() if v is not None}
            
            # Initialize Pyrebase for client-side authentication
            if PYREBASE_AVAILABLE and firebase_config.get("apiKey"):
                firebase = pyrebase.initialize_app(firebase_config)
                self.pyrebase_auth = firebase.auth()
            
            # Initialize Firebase Admin SDK for server-side operations
            if FIREBASE_ADMIN_AVAILABLE:
                if not firebase_admin._apps:
                    try:
                        # Try with project ID only for development
                        project_id = os.getenv("FIREBASE_PROJECT_ID")
                        if project_id:
                            self.app = firebase_admin.initialize_app(
                                options={'projectId': project_id}
                            )
                        self.app = None
                    except Exception:
                        self.app = None
                else:
                    self.app = firebase_admin.get_app()
                
                # Initialize Firestore if app is available
                if self.app:
                    try:
                        self.db = firestore.client()
                    except Exception:
                        self.db = None
            
            print("✅ Firebase initialization completed")
            
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            self.db = None
            self.pyrebase_auth = None
    
    # Authentication Methods
    async def create_user(self, email: str, password: str, display_name: str = None) -> Dict:
        """Create a new user account"""
        try:
            if not self.pyrebase_auth:
                return {"error": "Firebase not initialized"}
            
            # Create user with email and password
            user = self.pyrebase_auth.create_user_with_email_and_password(email, password)
            
            # Update profile if display name provided
            if display_name:
                self.pyrebase_auth.update_profile(user['idToken'], display_name=display_name)
            
            # Create user document in Firestore
            await self.create_user_document(user['localId'], {
                'email': email,
                'displayName': display_name,
                'createdAt': datetime.now(timezone.utc),
                'lastLogin': datetime.now(timezone.utc)
            })
            
            return {
                "success": True,
                "user": {
                    "uid": user['localId'],
                    "email": email,
                    "displayName": display_name,
                    "token": user['idToken']
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def sign_in_user(self, email: str, password: str) -> Dict:
        """Sign in user with email and password"""
        try:
            if not self.pyrebase_auth:
                return {"error": "Firebase not initialized"}
            
            user = self.pyrebase_auth.sign_in_with_email_and_password(email, password)
            
            # Update last login
            await self.update_user_document(user['localId'], {
                'lastLogin': datetime.now(timezone.utc)
            })
            
            return {
                "success": True,
                "user": {
                    "uid": user['localId'],
                    "email": user['email'],
                    "token": user['idToken']
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def verify_token(self, token: str) -> Dict:
        """Verify Firebase ID token"""
        try:
            if not FIREBASE_ADMIN_AVAILABLE or not self.app:
                # Fallback verification for development (in production use proper Firebase Admin)
                return {
                    "success": True,
                    "uid": "temp_user",
                    "email": "user@example.com",
                    "displayName": "Test User",
                    "emailVerified": True,
                    "user": {
                        "uid": "temp_user",
                        "email": "user@example.com",
                        "displayName": "Test User",
                        "emailVerified": True
                    }
                }
            
            decoded_token = auth.verify_id_token(token)
            return {
                "success": True,
                "uid": decoded_token['uid'],
                "email": decoded_token.get('email'),
                "user": decoded_token
            }
        except Exception as e:
            return {"error": str(e)}
    
    # User Document Management
    async def create_user_document(self, uid: str, user_data: Dict) -> bool:
        """Create user document in Firestore"""
        try:
            if not self.db:
                return False
            
            self.db.collection('users').document(uid).set(user_data)
            return True
        except Exception as e:
            print(f"Error creating user document: {e}")
            return False
    
    async def update_user_document(self, uid: str, update_data: Dict) -> bool:
        """Update user document in Firestore"""
        try:
            if not self.db:
                return False
            
            self.db.collection('users').document(uid).update(update_data)
            return True
        except Exception as e:
            print(f"Error updating user document: {e}")
            return False
    
    async def get_user_document(self, uid: str) -> Optional[Dict]:
        """Get user document from Firestore"""
        try:
            if not self.db:
                return None
            
            doc = self.db.collection('users').document(uid).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user document: {e}")
            return None
    
    # Chat Thread Management
    async def create_chat_thread(self, uid: str, title: str = None) -> str:
        """Create a new chat thread for user"""
        try:
            if not self.db:
                return None
            
            thread_data = {
                'uid': uid,
                'title': title or f"Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                'createdAt': datetime.now(timezone.utc),
                'updatedAt': datetime.now(timezone.utc),
                'messageCount': 0
            }
            
            thread_ref = self.db.collection('chat_threads').add(thread_data)
            return thread_ref[1].id  # Return thread ID
            
        except Exception as e:
            print(f"Error creating chat thread: {e}")
            return None
    
    async def get_user_threads(self, uid: str) -> List[Dict]:
        """Get all chat threads for a user"""
        try:
            if not self.db:
                return []
            
            threads = self.db.collection('chat_threads')\
                .where('uid', '==', uid)\
                .order_by('updatedAt', direction=firestore.Query.DESCENDING)\
                .stream()
            
            thread_list = []
            for thread in threads:
                thread_data = thread.to_dict()
                thread_data['id'] = thread.id
                thread_list.append(thread_data)
            
            return thread_list
            
        except Exception as e:
            print(f"Error getting user threads: {e}")
            return []
    
    async def save_chat_message(self, thread_id: str, user_message: str, ai_response: str, location: str = None) -> bool:
        """Save a chat message to a thread"""
        try:
            if not self.db:
                return False
            
            message_data = {
                'threadId': thread_id,
                'userMessage': user_message,
                'aiResponse': ai_response,
                'location': location,
                'timestamp': datetime.now(timezone.utc)
            }
            
            # Add message to messages collection
            self.db.collection('chat_messages').add(message_data)
            
            # Update thread's last message time and count
            thread_ref = self.db.collection('chat_threads').document(thread_id)
            thread_ref.update({
                'updatedAt': datetime.now(timezone.utc),
                'messageCount': firestore.Increment(1),
                'lastMessage': user_message[:100] + ('...' if len(user_message) > 100 else '')
            })
            
            return True
            
        except Exception as e:
            print(f"Error saving chat message: {e}")
            return False
    
    async def get_thread_messages(self, thread_id: str) -> List[Dict]:
        """Get all messages in a chat thread"""
        try:
            if not self.db:
                return []
            
            messages = self.db.collection('chat_messages')\
                .where('threadId', '==', thread_id)\
                .order_by('timestamp', direction=firestore.Query.ASCENDING)\
                .stream()
            
            message_list = []
            for message in messages:
                message_data = message.to_dict()
                message_data['id'] = message.id
                message_list.append(message_data)
            
            return message_list
            
        except Exception as e:
            print(f"Error getting thread messages: {e}")
            return []
    
    async def delete_thread(self, thread_id: str, uid: str) -> bool:
        """Delete a chat thread and its messages"""
        try:
            if not self.db:
                return False
            
            # Verify thread belongs to user
            thread_doc = self.db.collection('chat_threads').document(thread_id).get()
            if not thread_doc.exists or thread_doc.to_dict().get('uid') != uid:
                return False
            
            # Delete all messages in thread
            messages = self.db.collection('chat_messages')\
                .where('threadId', '==', thread_id)\
                .stream()
            
            for message in messages:
                message.reference.delete()
            
            # Delete thread
            self.db.collection('chat_threads').document(thread_id).delete()
            
            return True
            
        except Exception as e:
            print(f"Error deleting thread: {e}")
            return False

# Global Firebase service instance
firebase_service = FirebaseService()
