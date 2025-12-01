/**
 * Countdown Timer for Verification Page
 * Handles countdown display and automatic redirect
 */

// Configuration
const DEFAULT_COUNTDOWN = 5; // seconds

// State
let countdownInterval = null;
let remainingSeconds = DEFAULT_COUNTDOWN;

/**
 * Initialize countdown timer
 * @param {string} redirectUrl - URL to redirect to after countdown
 * @param {number} seconds - Countdown duration in seconds
 */
function initCountdown(redirectUrl, seconds = DEFAULT_COUNTDOWN) {
    remainingSeconds = seconds;
    
    const countdownElement = document.getElementById('countdown');
    
    if (!countdownElement) {
        console.error('Countdown element not found');
        return;
    }
    
    // Display initial countdown
    updateCountdownDisplay(countdownElement, remainingSeconds);
    
    // Start countdown
    countdownInterval = setInterval(() => {
        remainingSeconds--;
        
        // Update display
        updateCountdownDisplay(countdownElement, remainingSeconds);
        
        // Check if countdown finished
        if (remainingSeconds <= 0) {
            clearInterval(countdownInterval);
            performRedirect(redirectUrl);
        }
    }, 1000);
}

/**
 * Update countdown display
 * @param {HTMLElement} element - Countdown element
 * @param {number} seconds - Remaining seconds
 */
function updateCountdownDisplay(element, seconds) {
    element.textContent = seconds;
    
    // Add animation class
    element.classList.remove('pulse');
    void element.offsetWidth; // Trigger reflow
    element.classList.add('pulse');
}

/**
 * Perform redirect to bot
 * @param {string} url - Redirect URL
 */
function performRedirect(url) {
    console.log('Redirecting to:', url);
    window.location.href = url;
}

/**
 * Cancel countdown and redirect immediately
 */
function skipCountdown() {
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }
    
    const redirectUrl = document.getElementById('countdown').dataset.redirectUrl;
    
    if (redirectUrl) {
        performRedirect(redirectUrl);
    }
}

/**
 * Add event listeners
 */
function setupEventListeners() {
    // Skip button (if exists)
    const skipButton = document.getElementById('skip-button');
    if (skipButton) {
        skipButton.addEventListener('click', skipCountdown);
    }
    
    // Click anywhere to skip (optional)
    const containerElement = document.querySelector('.container');
    if (containerElement && containerElement.dataset.clickToSkip === 'true') {
        containerElement.addEventListener('click', skipCountdown);
        containerElement.style.cursor = 'pointer';
    }
}

/**
 * Format time remaining
 * @param {number} seconds - Seconds to format
 * @returns {string} Formatted time string
 */
function formatTime(seconds) {
    if (seconds < 60) {
        return `${seconds}s`;
    }
    
    const minutes = Math.floor(seconds / 60);
    const remainingSecs = seconds % 60;
    
    return `${minutes}m ${remainingSecs}s`;
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    const container = document.querySelector('.container');
    
    if (container) {
        container.innerHTML = `
            <div class="error-icon">❌</div>
            <h1>Error</h1>
            <p class="message">${message}</p>
            <button class="button" onclick="window.history.back()">Go Back</button>
        `;
        container.classList.add('error-container');
    }
}

/**
 * Validate redirect URL
 * @param {string} url - URL to validate
 * @returns {boolean} True if valid
 */
function isValidRedirectUrl(url) {
    if (!url) return false;
    
    try {
        const urlObj = new URL(url);
        // Only allow t.me domain
        return urlObj.hostname === 't.me';
    } catch (e) {
        return false;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const countdownElement = document.getElementById('countdown');
    
    if (countdownElement) {
        const redirectUrl = countdownElement.dataset.redirectUrl;
        const seconds = parseInt(countdownElement.dataset.seconds) || DEFAULT_COUNTDOWN;
        
        // Validate redirect URL
        if (!isValidRedirectUrl(redirectUrl)) {
            showError('Invalid redirect URL');
            return;
        }
        
        // Setup event listeners
        setupEventListeners();
        
        // Start countdown
        initCountdown(redirectUrl, seconds);
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }
});

// Export functions for external use (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initCountdown,
        skipCountdown,
        formatTime
    };
}