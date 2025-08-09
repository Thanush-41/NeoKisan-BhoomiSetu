// Firebase Configuration and Initialization
// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth, GoogleAuthProvider, signInWithPopup, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged } from "firebase/auth";
import { getFirestore, collection, addDoc, getDocs, doc, deleteDoc, updateDoc, query, orderBy, where } from "firebase/firestore";

// Dynamic Firebase configuration - fetch from server API for security
async function getFirebaseConfig() {
  try {
    const response = await fetch('/api/firebase-config');
    const firebaseConfig = await response.json();
    return firebaseConfig;
  } catch (error) {
    console.error('Failed to fetch Firebase config:', error);
    throw error;
  }
}

// Initialize Firebase with dynamic configuration
async function initializeFirebaseServices() {
  try {
    const firebaseConfig = await getFirebaseConfig();
    const app = initializeApp(firebaseConfig);
    const analytics = getAnalytics(app);
    const auth = getAuth(app);
    const db = getFirestore(app);
    const googleProvider = new GoogleAuthProvider();
    
    return {
      app,
      analytics,
      auth,
      db,
      googleProvider,
      signInWithPopup,
      signInWithEmailAndPassword,
      createUserWithEmailAndPassword,
      signOut,
      onAuthStateChanged,
      collection,
      addDoc,
      getDocs,
      doc,
      deleteDoc,
      updateDoc,
      query,
      orderBy,
      where
    };
  } catch (error) {
    console.error('Failed to initialize Firebase services:', error);
    throw error;
  }
}

// Export the initialization function
export { initializeFirebaseServices };

// Firebase Authentication Helper Functions
export class FirebaseAuth {
  
  // Google Sign In
  static async signInWithGoogle() {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      return {
        success: true,
        user: result.user,
        token: await result.user.getIdToken()
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Email/Password Sign In
  static async signInWithEmail(email, password) {
    try {
      const result = await signInWithEmailAndPassword(auth, email, password);
      return {
        success: true,
        user: result.user,
        token: await result.user.getIdToken()
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Email/Password Registration
  static async registerWithEmail(email, password, displayName = null) {
    try {
      const result = await createUserWithEmailAndPassword(auth, email, password);
      
      // Update profile if display name provided
      if (displayName && result.user.updateProfile) {
        await result.user.updateProfile({ displayName });
      }
      
      return {
        success: true,
        user: result.user,
        token: await result.user.getIdToken()
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Sign Out
  static async signOut() {
    try {
      await signOut(auth);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Get Current User
  static getCurrentUser() {
    return auth.currentUser;
  }

  // Listen to auth state changes
  static onAuthStateChanged(callback) {
    return onAuthStateChanged(auth, callback);
  }
}

// Firebase Firestore Helper Functions for Chat Threads
export class FirebaseChatService {
  
  // Create new chat thread
  static async createThread(userId, title = null) {
    try {
      const thread = {
        userId: userId,
        title: title || `Chat ${new Date().toLocaleDateString()}`,
        createdAt: new Date(),
        updatedAt: new Date(),
        messageCount: 0,
        lastMessage: null
      };
      
      const docRef = await addDoc(collection(db, 'chatThreads'), thread);
      return {
        success: true,
        threadId: docRef.id,
        thread: { id: docRef.id, ...thread }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Get user's chat threads
  static async getUserThreads(userId) {
    try {
      const q = query(
        collection(db, 'chatThreads'),
        where('userId', '==', userId),
        orderBy('updatedAt', 'desc')
      );
      
      const querySnapshot = await getDocs(q);
      const threads = [];
      
      querySnapshot.forEach((doc) => {
        threads.push({
          id: doc.id,
          ...doc.data(),
          createdAt: doc.data().createdAt?.toDate(),
          updatedAt: doc.data().updatedAt?.toDate()
        });
      });
      
      return {
        success: true,
        threads: threads
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Add message to thread
  static async addMessageToThread(threadId, message, isUser = true) {
    try {
      // Add message to messages subcollection
      const messageData = {
        content: message,
        isUser: isUser,
        timestamp: new Date(),
        threadId: threadId
      };
      
      await addDoc(collection(db, 'chatThreads', threadId, 'messages'), messageData);
      
      // Update thread metadata
      const threadRef = doc(db, 'chatThreads', threadId);
      await updateDoc(threadRef, {
        lastMessage: message.substring(0, 100) + (message.length > 100 ? '...' : ''),
        updatedAt: new Date(),
        messageCount: (await this.getThreadMessageCount(threadId)) + 1
      });
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Get thread messages
  static async getThreadMessages(threadId) {
    try {
      const q = query(
        collection(db, 'chatThreads', threadId, 'messages'),
        orderBy('timestamp', 'asc')
      );
      
      const querySnapshot = await getDocs(q);
      const messages = [];
      
      querySnapshot.forEach((doc) => {
        messages.push({
          id: doc.id,
          ...doc.data(),
          timestamp: doc.data().timestamp?.toDate()
        });
      });
      
      return {
        success: true,
        messages: messages
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Delete thread
  static async deleteThread(threadId) {
    try {
      // Delete all messages in the thread
      const messagesQuery = query(collection(db, 'chatThreads', threadId, 'messages'));
      const messagesSnapshot = await getDocs(messagesQuery);
      
      const deletePromises = messagesSnapshot.docs.map(messageDoc => 
        deleteDoc(doc(db, 'chatThreads', threadId, 'messages', messageDoc.id))
      );
      await Promise.all(deletePromises);
      
      // Delete the thread document
      await deleteDoc(doc(db, 'chatThreads', threadId));
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Helper: Get thread message count
  static async getThreadMessageCount(threadId) {
    try {
      const messagesSnapshot = await getDocs(collection(db, 'chatThreads', threadId, 'messages'));
      return messagesSnapshot.size;
    } catch (error) {
      return 0;
    }
  }
}

// Make services available globally for legacy code compatibility
window.FirebaseAuth = FirebaseAuth;
window.FirebaseChatService = FirebaseChatService;
window.firebaseAuth = auth;
window.firebaseDb = db;

console.log('Firebase initialized successfully for BhoomiSetu!');
