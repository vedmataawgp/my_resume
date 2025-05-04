// SmartSpend Main JavaScript

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggler
    initThemeToggler();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize popovers
    initPopovers();
    
    // Auto-dismiss alerts after 5 seconds
    autoHideAlerts();
    
    // Add active class to current navigation item
    highlightCurrentNavItem();
    
    // Mobile navigation enhancement
    enhanceMobileNavigation();
});

/**
 * Initialize theme toggler functionality
 */
function initThemeToggler() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeText = document.getElementById('theme-text');
    
    if (themeToggleBtn) {
        // Check for saved theme preference or respect OS preference
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Set initial theme
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            document.body.setAttribute('data-bs-theme', 'dark');
            updateThemeToggleUI(true);
        }
        
        // Toggle theme when button is clicked
        themeToggleBtn.addEventListener('click', function() {
            const isDark = document.body.getAttribute('data-bs-theme') === 'dark';
            const newTheme = isDark ? 'light' : 'dark';
            
            document.body.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            updateThemeToggleUI(!isDark);
        });
    }
    
    // Helper function to update theme toggle button UI
    function updateThemeToggleUI(isDark) {
        if (!themeToggleBtn || !themeText) return;
        
        const themeIcon = themeToggleBtn.querySelector('i');
        
        if (isDark) {
            themeIcon.className = 'fas fa-sun me-1';
            themeText.textContent = 'Light Mode';
        } else {
            themeIcon.className = 'fas fa-moon me-1';
            themeText.textContent = 'Dark Mode';
        }
    }
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

/**
 * Initialize Bootstrap popovers
 */
function initPopovers() {
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
}

/**
 * Auto-hide alerts after a delay
 */
function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Highlight current navigation item
 */
function highlightCurrentNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        }
    });
}

/**
 * Enhance mobile navigation experience
 */
function enhanceMobileNavigation() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when a nav item is clicked
        const navItems = navbarCollapse.querySelectorAll('.nav-link');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                if (window.innerWidth < 992) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                    bsCollapse.hide();
                }
            });
        });
    }
}

/**
 * Format currency values
 * @param {number} value - The value to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

/**
 * Format percentage values
 * @param {number} value - The value to format
 * @returns {string} Formatted percentage string
 */
function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value / 100);
}

/**
 * Format date values
 * @param {string} dateString - The date string to format
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
}

/**
 * Calculate days between two dates
 * @param {Date} startDate - The start date
 * @param {Date} endDate - The end date
 * @returns {number} Number of days between dates
 */
function daysBetween(startDate, endDate) {
    const oneDay = 24 * 60 * 60 * 1000; // milliseconds in a day
    return Math.round(Math.abs((startDate - endDate) / oneDay));
}

/**
 * Confirm action with a modal dialog
 * @param {string} message - Confirmation message
 * @returns {boolean} True if confirmed, false otherwise
 */
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to perform this action?');
}
