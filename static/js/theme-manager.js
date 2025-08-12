// Theme Management for BhoomiSetu
class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('bhoomi-theme') || 'light';
        this.init();
    }

    init() {
        // Apply stored theme on page load
        this.applyTheme(this.currentTheme);
        
        // Update toggle button state
        this.updateToggleButton();
        
        // Add event listeners
        this.addEventListeners();
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        
        // Store preference
        localStorage.setItem('bhoomi-theme', theme);
        
        // Force update CSS variables on the root element
        const root = document.documentElement;
        if (theme === 'dark') {
            root.style.setProperty('--primary-green', '#4CAF50');
            root.style.setProperty('--accent-yellow', '#1a1a1a');
            root.style.setProperty('--light-bg', '#121212');
            root.style.setProperty('--dark-text', '#e0e0e0');
            root.style.setProperty('--muted-text', '#b0b0b0');
            root.style.setProperty('--card-bg', '#1e1e1e');
            root.style.setProperty('--navbar-bg', '#1f1f1f');
            root.style.setProperty('--border-color', '#333');
        } else {
            root.style.setProperty('--primary-green', '#2E7D32');
            root.style.setProperty('--accent-yellow', '#fefcf5');
            root.style.setProperty('--light-bg', '#fefcf5');
            root.style.setProperty('--dark-text', '#212121');
            root.style.setProperty('--muted-text', '#555');
            root.style.setProperty('--card-bg', '#ffffff');
            root.style.setProperty('--navbar-bg', '#ffffff');
            root.style.setProperty('--border-color', '#eee');
        }
        
        // Update meta theme-color for mobile browsers
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#121212' : '#ffffff');
        }
        
        // Force body background update
        document.body.style.backgroundColor = theme === 'dark' ? '#121212' : '#fefcf5';
        document.body.style.color = theme === 'dark' ? '#e0e0e0' : '#212121';
        
        // Dispatch custom event for components that need to react to theme changes
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        this.updateToggleButton();
        
        // Show brief notification
        this.showThemeChangeNotification(newTheme);
    }

    updateToggleButton() {
        // Update all theme toggle buttons on the page
        const toggleButtons = ['themeToggle', 'themeToggleUser'];
        const toggleIcons = ['themeIcon', 'themeIconUser'];
        
        toggleButtons.forEach((buttonId, index) => {
            const toggleButton = document.getElementById(buttonId);
            const toggleIcon = document.getElementById(toggleIcons[index]);
            
            if (toggleButton && toggleIcon) {
                if (this.currentTheme === 'dark') {
                    toggleIcon.className = 'fas fa-sun';
                    toggleButton.title = 'Switch to Light Mode';
                } else {
                    toggleIcon.className = 'fas fa-moon';
                    toggleButton.title = 'Switch to Dark Mode';
                }
            }
        });
    }

    addEventListeners() {
        // Theme toggle buttons - handle multiple buttons
        const toggleButtons = ['themeToggle', 'themeToggleUser'];
        
        toggleButtons.forEach(buttonId => {
            const toggleButton = document.getElementById(buttonId);
            if (toggleButton) {
                toggleButton.addEventListener('click', () => this.toggleTheme());
            }
        });

        // Listen for system theme changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addListener((e) => {
                // Only auto-switch if user hasn't manually set a preference
                if (!localStorage.getItem('bhoomi-theme')) {
                    this.applyTheme(e.matches ? 'dark' : 'light');
                    this.updateToggleButton();
                }
            });
        }
    }

    showThemeChangeNotification(theme) {
        // Create a small toast notification
        const toast = document.createElement('div');
        toast.className = 'position-fixed top-0 end-0 m-3 alert alert-success alert-dismissible fade show';
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            <i class="fas fa-${theme === 'dark' ? 'moon' : 'sun'}"></i>
            Switched to ${theme} mode
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 3000);
    }

    // Get current theme
    getTheme() {
        return this.currentTheme;
    }

    // Force set theme (useful for specific pages or components)
    setTheme(theme) {
        if (theme === 'light' || theme === 'dark') {
            this.applyTheme(theme);
            this.updateToggleButton();
        }
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.themeManager = new ThemeManager();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
