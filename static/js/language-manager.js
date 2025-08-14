/**
 * Language Manager for BhoomiSetu
 * Handles language switching, persistence, and initialization
 */

class LanguageManager {
    constructor() {
        this.currentLanguage = this.getCurrentLanguage();
        this.init();
    }

    /**
     * Initialize language manager
     */
    init() {
        // Auto-redirect to stored language if URL doesn't have language parameter
        this.checkAndRedirectToStoredLanguage();
        
        // Initialize dropdown interactions
        this.initializeDropdownInteractions();
        
        // Add language change listeners
        this.addLanguageChangeListeners();
    }

    /**
     * Get current language from URL or localStorage
     */
    getCurrentLanguage() {
        const urlParams = new URLSearchParams(window.location.search);
        const urlLang = urlParams.get('lang');
        const storedLang = localStorage.getItem('selectedLanguage');
        
        return urlLang || storedLang || 'en';
    }

    /**
     * Get stored language preference
     */
    getStoredLanguage() {
        return localStorage.getItem('selectedLanguage') || 'en';
    }

    /**
     * Store language preference
     */
    storeLanguage(langCode) {
        localStorage.setItem('selectedLanguage', langCode);
    }

    /**
     * Check if we should redirect to stored language
     */
    checkAndRedirectToStoredLanguage() {
        const urlParams = new URLSearchParams(window.location.search);
        const urlLang = urlParams.get('lang');
        const storedLang = this.getStoredLanguage();
        
        // If no URL language parameter but we have stored preference, redirect
        if (!urlLang && storedLang && storedLang !== 'en') {
            const url = new URL(window.location);
            url.searchParams.set('lang', storedLang);
            window.location.href = url.toString();
        }
    }

    /**
     * Change language with enhanced UX
     */
    changeLanguage(langCode) {
        // Validate language code
        const supportedLanguages = [
            'en', 'hi', 'te', 'kn', 'gu', 'pa', 
            'ta', 'ml', 'bn', 'mr', 'or', 'as'
        ];
        
        if (!supportedLanguages.includes(langCode)) {
            console.warn(`Unsupported language: ${langCode}`);
            return;
        }

        // Store the selected language preference
        this.storeLanguage(langCode);
        
        // Show loading indicator
        this.showLanguageChangeLoading();
        
        // Construct new URL with language parameter
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('lang', langCode);
        
        // Add a small delay for better UX
        setTimeout(() => {
            window.location.href = currentUrl.toString();
        }, 300);
    }

    /**
     * Show loading indicator during language change
     */
    showLanguageChangeLoading() {
        const dropdown = document.getElementById('languageDropdown');
        if (dropdown) {
            const originalHTML = dropdown.innerHTML;
            dropdown.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span class="d-none d-xl-inline ms-1">Switching...</span>';
            dropdown.disabled = true;
            
            // Store original content in case we need to restore it
            dropdown.dataset.originalContent = originalHTML;
        }
    }

    /**
     * Initialize dropdown interactions
     */
    initializeDropdownInteractions() {
        const languageDropdown = document.getElementById('languageDropdown');
        if (!languageDropdown) return;

        // Ensure Bootstrap dropdown is initialized
        if (!bootstrap.Dropdown.getInstance(languageDropdown)) {
            new bootstrap.Dropdown(languageDropdown);
        }

        // Add keyboard navigation
        this.addKeyboardNavigation();
        
        // Add hover effects
        this.addHoverEffects();
    }

    /**
     * Add keyboard navigation for language dropdown
     */
    addKeyboardNavigation() {
        const dropdownMenu = document.querySelector('#languageDropdown + .dropdown-menu');
        if (!dropdownMenu) return;

        dropdownMenu.addEventListener('keydown', (event) => {
            const items = Array.from(dropdownMenu.querySelectorAll('.dropdown-item:not(.disabled)'));
            let currentIndex = items.findIndex(item => item === document.activeElement);
            
            switch (event.key) {
                case 'ArrowDown':
                    event.preventDefault();
                    currentIndex = (currentIndex + 1) % items.length;
                    items[currentIndex].focus();
                    break;
                case 'ArrowUp':
                    event.preventDefault();
                    currentIndex = currentIndex <= 0 ? items.length - 1 : currentIndex - 1;
                    items[currentIndex].focus();
                    break;
                case 'Enter':
                    event.preventDefault();
                    if (document.activeElement.onclick) {
                        document.activeElement.click();
                    }
                    break;
                case 'Escape':
                    document.getElementById('languageDropdown').click();
                    document.getElementById('languageDropdown').focus();
                    break;
            }
        });
    }

    /**
     * Add hover effects to language items
     */
    addHoverEffects() {
        const languageItems = document.querySelectorAll('.language-item');
        languageItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(2px)';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0)';
            });
        });
    }

    /**
     * Add event listeners for language changes
     */
    addLanguageChangeListeners() {
        // Listen for language change events from other sources
        window.addEventListener('languageChange', (event) => {
            this.changeLanguage(event.detail.language);
        });
    }

    /**
     * Get language display name from code
     */
    getLanguageDisplayName(langCode) {
        const languages = {
            'en': 'English',
            'hi': 'हिंदी (Hindi)',
            'te': 'తెలుగు (Telugu)', 
            'kn': 'ಕನ್ನಡ (Kannada)',
            'gu': 'ગુજરાતી (Gujarati)',
            'pa': 'ਪੰਜਾਬੀ (Punjabi)',
            'ta': 'தமிழ் (Tamil)',
            'ml': 'മലയാളം (Malayalam)',
            'bn': 'বাংলা (Bengali)',
            'mr': 'मराठी (Marathi)',
            'or': 'ଓଡ଼ିଆ (Odia)',
            'as': 'অসমীয়া (Assamese)'
        };
        
        return languages[langCode] || langCode;
    }

    /**
     * Trigger a custom language change event
     */
    triggerLanguageChange(langCode) {
        const event = new CustomEvent('languageChange', {
            detail: { language: langCode }
        });
        window.dispatchEvent(event);
    }
}

// Global language change function for backward compatibility
function changeLanguage(langCode) {
    if (window.languageManager) {
        window.languageManager.changeLanguage(langCode);
    } else {
        // Fallback implementation
        localStorage.setItem('selectedLanguage', langCode);
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('lang', langCode);
        window.location.href = currentUrl.toString();
    }
}

// Initialize language manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.languageManager = new LanguageManager();
    console.log('Language Manager initialized');
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LanguageManager;
}
