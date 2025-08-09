// Shared Authentication State Manager
// This ensures authentication state is synchronized across all pages

class AuthStateManager {
    constructor() {
        this.listeners = [];
        this.currentUser = null;
        this.isFirebaseReady = false;
        
        // Listen for storage events (when user logs in/out on another tab)
        window.addEventListener('storage', (e) => {
            if (e.key === 'firebase_user') {
                this.handleStorageChange(e);
            }
        });
        
        // Listen for custom auth events
        window.addEventListener('authStateChanged', (e) => {
            this.handleAuthStateChange(e.detail);
        });
    }
    
    // Initialize Firebase and set up auth listener
    async initializeAuth() {
        try {
            // Wait for Firebase to be initialized
            await this.waitForFirebase();
            
            // Set up Firebase auth state listener
            if (window.firebaseAuth && window.onAuthStateChanged) {
                window.onAuthStateChanged(window.firebaseAuth, (user) => {
                    this.handleFirebaseAuthChange(user);
                });
                this.isFirebaseReady = true;
                console.log('✅ AuthStateManager: Firebase auth listener set up');
            }
        } catch (error) {
            console.error('❌ AuthStateManager: Failed to initialize:', error);
        }
    }
    
    // Wait for Firebase to be ready
    async waitForFirebase() {
        return new Promise((resolve, reject) => {
            let attempts = 0;
            const maxAttempts = 50; // 5 seconds total
            
            const checkFirebase = () => {
                if (window.firebaseAuth && window.onAuthStateChanged) {
                    resolve();
                } else if (attempts < maxAttempts) {
                    attempts++;
                    setTimeout(checkFirebase, 100);
                } else {
                    reject(new Error('Firebase authentication not available'));
                }
            };
            
            checkFirebase();
        });
    }
    
    // Handle Firebase auth state changes
    handleFirebaseAuthChange(user) {
        if (user) {
            const userData = {
                uid: user.uid,
                email: user.email,
                displayName: user.displayName || user.email.split('@')[0],
                photoURL: user.photoURL
            };
            
            this.setUser(userData);
            
            // Store in localStorage for cross-tab synchronization
            localStorage.setItem('firebase_user', JSON.stringify(userData));
            
            console.log('✅ AuthStateManager: User signed in:', userData.email);
        } else {
            this.setUser(null);
            localStorage.removeItem('firebase_user');
            console.log('✅ AuthStateManager: User signed out');
        }
    }
    
    // Handle storage changes (cross-tab sync)
    handleStorageChange(event) {
        if (event.key === 'firebase_user') {
            const userData = event.newValue ? JSON.parse(event.newValue) : null;
            this.setUser(userData, false); // Don't trigger storage update again
        }
    }
    
    // Handle custom auth events
    handleAuthStateChange(userData) {
        this.setUser(userData);
    }
    
    // Set current user and notify listeners
    setUser(userData, updateStorage = true) {
        this.currentUser = userData;
        window.currentUser = userData; // Global reference
        
        // Update localStorage if needed
        if (updateStorage) {
            if (userData) {
                localStorage.setItem('firebase_user', JSON.stringify(userData));
            } else {
                localStorage.removeItem('firebase_user');
            }
        }
        
        // Notify all listeners
        this.notifyListeners(userData);
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('globalAuthStateChanged', {
            detail: userData
        }));
    }
    
    // Add auth state listener
    addListener(callback) {
        this.listeners.push(callback);
        
        // Immediately call with current state if available
        if (this.currentUser !== null) {
            callback(this.currentUser);
        }
    }
    
    // Remove auth state listener
    removeListener(callback) {
        this.listeners = this.listeners.filter(listener => listener !== callback);
    }
    
    // Notify all listeners
    notifyListeners(userData) {
        this.listeners.forEach(callback => {
            try {
                callback(userData);
            } catch (error) {
                console.error('AuthStateManager listener error:', error);
            }
        });
    }
    
    // Get current user
    getCurrentUser() {
        return this.currentUser;
    }
    
    // Check if user is logged in
    isLoggedIn() {
        return this.currentUser !== null;
    }
    
    // Initialize from stored state
    initializeFromStorage() {
        try {
            const storedUser = localStorage.getItem('firebase_user');
            if (storedUser) {
                const userData = JSON.parse(storedUser);
                this.setUser(userData, false);
                console.log('✅ AuthStateManager: Restored user from storage:', userData.email);
            }
        } catch (error) {
            console.error('AuthStateManager: Error restoring from storage:', error);
            localStorage.removeItem('firebase_user');
        }
    }
    
    // Update UI based on auth state
    updateUI(userData) {
        try {
            const authButtonsEl = document.getElementById('authButtons');
            const userMenuEl = document.getElementById('userMenu');
            const userNameEl = document.getElementById('userName');
            const userEmailEl = document.getElementById('userEmail');
            const threadControlsEl = document.getElementById('threadControls'); // For chat page
            
            if (userData) {
                // User is logged in
                if (authButtonsEl) {
                    authButtonsEl.style.setProperty('display', 'none', 'important');
                }
                if (userMenuEl) {
                    userMenuEl.style.setProperty('display', 'block', 'important');
                }
                if (userNameEl) {
                    userNameEl.textContent = userData.displayName || userData.email.split('@')[0];
                }
                if (userEmailEl) {
                    userEmailEl.textContent = userData.email;
                }
                if (threadControlsEl) {
                    threadControlsEl.style.setProperty('display', 'flex', 'important');
                }
                console.log('✅ UI updated for logged in user:', userData.email);
            } else {
                // User is logged out
                if (authButtonsEl) {
                    authButtonsEl.style.setProperty('display', 'flex', 'important');
                }
                if (userMenuEl) {
                    userMenuEl.style.setProperty('display', 'none', 'important');
                }
                if (threadControlsEl) {
                    threadControlsEl.style.setProperty('display', 'none', 'important');
                }
                console.log('✅ UI updated for logged out user');
            }
        } catch (error) {
            console.error('AuthStateManager UI update error:', error);
        }
    }
}

// Create global instance
window.authStateManager = new AuthStateManager();

// Initialize from storage immediately
window.authStateManager.initializeFromStorage();

// Set up UI listener
window.authStateManager.addListener((userData) => {
    window.authStateManager.updateUI(userData);
});

// Initialize Firebase auth when ready
document.addEventListener('DOMContentLoaded', () => {
    window.authStateManager.initializeAuth();
});

console.log('✅ AuthStateManager loaded and ready');
