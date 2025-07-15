/*
Interactive AI Features - Simple JavaScript Handlers
Basic button functionality for refresh, validate, and usage tracking
*/

// Global state for usage tracking
let usageStats = {
    today_calls: 0,
    remaining_calls: 50,
    today_cost: 0
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Interactive AI features loaded');
    loadUsageStats();
    
    // Update usage counter every 30 seconds
    setInterval(loadUsageStats, 30000);
});

// Simple refresh function
async function refreshStock(ticker) {
    const button = document.querySelector(`[onclick="refreshStock('${ticker}')"]`);
    const originalText = button ? button.innerHTML : '';
    
    try {
        // Update button state
        if (button) {
            button.innerHTML = '🔄 Refreshing...';
            button.disabled = true;
        }
        
        // Call API
        const response = await fetch(`/api/force_refresh/${ticker}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Update usage stats
            usageStats = data.usage || usageStats;
            updateUsageDisplay();
            
            // Show success message
            showNotification(`✅ ${ticker} analysis refreshed`, 'success');
            
            // Update the stock card content if available
            const stockCard = document.querySelector(`[data-ticker="${ticker}"]`);
            if (stockCard && data.analysis) {
                updateStockCard(stockCard, data.analysis);
            }
            
        } else {
            throw new Error(data.error || 'Refresh failed');
        }
        
    } catch (error) {
        console.error('Refresh error:', error);
        showNotification(`❌ ${ticker} refresh failed: ${error.message}`, 'error');
    } finally {
        // Restore button state
        if (button) {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }
}

// Simple thesis validation
async function validateThesis(ticker) {
    const button = document.querySelector(`[onclick="validateThesis('${ticker}')"]`);
    const originalText = button ? button.innerHTML : '';
    
    try {
        // Update button state
        if (button) {
            button.innerHTML = '🤔 Validating...';
            button.disabled = true;
        }
        
        // Call API
        const response = await fetch(`/api/validate_thesis/${ticker}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Update usage stats
            usageStats = data.usage || usageStats;
            updateUsageDisplay();
            
            // Show validation result
            const statusEmoji = {
                'CONFIRMED': '✅',
                'WEAKENED': '⚠️', 
                'INVALIDATED': '❌',
                'UNKNOWN': '❓'
            };
            
            const emoji = statusEmoji[data.status] || '❓';
            showNotification(`${emoji} ${ticker} thesis: ${data.status}`, 'info');
            
            // Update stock card with validation result
            const stockCard = document.querySelector(`[data-ticker="${ticker}"]`);
            if (stockCard) {
                updateValidationStatus(stockCard, data.status, data.explanation);
            }
            
        } else {
            throw new Error(data.error || 'Validation failed');
        }
        
    } catch (error) {
        console.error('Validation error:', error);
        showNotification(`❌ ${ticker} validation failed: ${error.message}`, 'error');
    } finally {
        // Restore button state
        if (button) {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }
}

// Load and display usage statistics
async function loadUsageStats() {
    try {
        const response = await fetch('/api/usage_stats');
        const data = await response.json();
        
        if (response.ok && data.success) {
            usageStats = data.stats;
            updateUsageDisplay();
        }
        
    } catch (error) {
        console.log('Usage stats error (non-critical):', error);
    }
}

// Update usage display elements
function updateUsageDisplay() {
    // Update call counter
    const callCountElement = document.getElementById('call-count');
    if (callCountElement) {
        callCountElement.textContent = usageStats.today_calls || 0;
    }
    
    // Update remaining calls
    const remainingElement = document.getElementById('remaining-calls');
    if (remainingElement) {
        remainingElement.textContent = usageStats.remaining_calls || 0;
    }
    
    // Update cost
    const costElement = document.getElementById('today-cost');
    if (costElement) {
        costElement.textContent = `$${(usageStats.today_cost || 0).toFixed(3)}`;
    }
    
    // Update limit warning
    if (usageStats.remaining_calls <= 5) {
        showNotification(`⚠️ Only ${usageStats.remaining_calls} API calls remaining today`, 'warning');
    }
}

// Simple notification system
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.getElementById('notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.id = 'notification';
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Update stock card with new analysis (if elements exist)
function updateStockCard(stockCard, analysis) {
    try {
        // Look for analysis content area
        const analysisArea = stockCard.querySelector('.analysis-content');
        if (analysisArea && typeof analysis === 'string') {
            analysisArea.innerHTML = `<div class="fresh-analysis">${analysis.substring(0, 200)}...</div>`;
        }
        
        // Add refresh timestamp
        const timestampArea = stockCard.querySelector('.timestamp');
        if (timestampArea) {
            timestampArea.textContent = `Refreshed: ${new Date().toLocaleTimeString()}`;
        }
        
    } catch (error) {
        console.log('Stock card update error (non-critical):', error);
    }
}

// Update validation status on stock card
function updateValidationStatus(stockCard, status, explanation) {
    try {
        // Look for validation status area
        let validationArea = stockCard.querySelector('.validation-status');
        
        // Create validation area if it doesn't exist
        if (!validationArea) {
            validationArea = document.createElement('div');
            validationArea.className = 'validation-status';
            stockCard.appendChild(validationArea);
        }
        
        // Update content
        const statusClass = status.toLowerCase();
        validationArea.innerHTML = `
            <div class="validation-result ${statusClass}">
                <strong>Thesis: ${status}</strong>
                <div class="validation-explanation">${explanation.substring(0, 100)}...</div>
            </div>
        `;
        
    } catch (error) {
        console.log('Validation update error (non-critical):', error);
    }
}

// Show usage stats modal (if requested)
function showUsageStats() {
    const modal = document.createElement('div');
    modal.className = 'usage-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>📊 API Usage Statistics</h3>
            <div class="usage-grid">
                <div>Today's Calls: <strong>${usageStats.today_calls || 0}</strong></div>
                <div>Remaining: <strong>${usageStats.remaining_calls || 0}</strong></div>
                <div>Today's Cost: <strong>$${(usageStats.today_cost || 0).toFixed(3)}</strong></div>
                <div>Total Cost: <strong>$${(usageStats.total_cost || 0).toFixed(2)}</strong></div>
            </div>
            <button onclick="this.closest('.usage-modal').remove()">Close</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Auto-close on background click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}