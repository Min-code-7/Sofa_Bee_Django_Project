// Notification functions
function showNotification(message, type = 'info', duration = 5000) {
    const notificationArea = document.getElementById('notification-area');
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to notification area
    notificationArea.innerHTML = ''; // Clear previous notifications
    notificationArea.appendChild(notification);
    notificationArea.style.display = 'block';
    
    // Auto-dismiss after duration
    if (duration > 0) {
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notificationArea.removeChild(notification);
                if (notificationArea.children.length === 0) {
                    notificationArea.style.display = 'none';
                }
            }, 150);
        }, duration);
    }
    
    return notification;
}

function showSuccessNotification(message, duration = 5000) {
    return showNotification(message, 'success', duration);
}

function showErrorNotification(message, duration = 5000) {
    return showNotification(message, 'danger', duration);
}

function showWarningNotification(message, duration = 5000) {
    return showNotification(message, 'warning', duration);
}

// Function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
