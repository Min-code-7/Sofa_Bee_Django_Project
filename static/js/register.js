document.addEventListener('DOMContentLoaded', function() {
    // Variables to track timers
    let cooldownTimer = null;
    let expiryTimer = null;
    let cooldownSeconds = 0;
    let expirySeconds = 0;

    // Format seconds to MM:SS
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
    }

    // Start cooldown timer
    function startCooldownTimer(seconds) {
        const sendCodeBtn = document.getElementById("send-code");
        const countdownTimer = document.getElementById("countdown-timer");
        
        // Disable button and show countdown
        sendCodeBtn.disabled = true;
        countdownTimer.style.display = "block";
        cooldownSeconds = seconds;
        
        // Update countdown every second
        cooldownTimer = setInterval(function() {
            cooldownSeconds--;
            countdownTimer.textContent = `Resend in ${cooldownSeconds}s`;
            
            if (cooldownSeconds <= 0) {
                // Enable button and hide countdown when timer ends
                clearInterval(cooldownTimer);
                sendCodeBtn.disabled = false;
                countdownTimer.style.display = "none";
            }
        }, 1000);
    }

    // Start expiry timer
    function startExpiryTimer() {
        const codeExpiry = document.getElementById("code-expiry");
        const expiryTimerElement = document.getElementById("expiry-timer");
        
        // Show expiry message
        codeExpiry.style.display = "block";
        expirySeconds = 5 * 60; // 5 minutes in seconds
        
        // Update expiry timer every second
        expiryTimer = setInterval(function() {
            expirySeconds--;
            expiryTimerElement.textContent = formatTime(expirySeconds);
            
            if (expirySeconds <= 0) {
                // Hide expiry message when timer ends
                clearInterval(expiryTimer);
                codeExpiry.style.display = "none";
            }
        }, 1000);
    }

    // Send verification code
    document.getElementById("send-code")?.addEventListener("click", function() {
        var email = document.querySelector("input[name='email']").value;
        if (!email) {
            alert("Please input email first!");
            return;
        }

        // Get CSRF token
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        fetch(window.verificationCodeUrl || "/users/send-verification-code/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrfToken,
            },
            body: "email=" + encodeURIComponent(email),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                if (data.seconds_left) {
                    startCooldownTimer(data.seconds_left);
                }
            } else {
                // Display debug code if available (for development only)
                if (data.debug_code) {
                    alert(`${data.message}\n\nError details: ${data.error_details || 'None'}`);
                    
                    // Add the verification code to the input field automatically in debug mode
                    document.getElementById("id_verification_code").value = data.debug_code;
                    
                    // Highlight the field to indicate it was auto-filled
                    document.getElementById("id_verification_code").style.backgroundColor = "#e8f0fe";
                    
                    // Add a debug notice
                    const codeField = document.getElementById("id_verification_code").parentNode;
                    const debugNotice = document.createElement("small");
                    debugNotice.className = "text-info";
                    debugNotice.textContent = "Code auto-filled in debug mode";
                    codeField.appendChild(debugNotice);
                } else {
                    alert(data.message);
                }
                
                // Clear any existing timers
                if (cooldownTimer) clearInterval(cooldownTimer);
                if (expiryTimer) clearInterval(expiryTimer);
                
                // Start new timers
                startCooldownTimer(60); // 1 minute cooldown
                startExpiryTimer(); // 5 minutes expiry
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while sending the verification code. Please try again.");
        });
    });

    // Check username availability
    let usernameCheckTimeout = null;
    document.getElementById("id_username")?.addEventListener("input", function() {
        const username = this.value.trim();
        const usernameFeedback = document.getElementById("username-feedback");
        
        // Clear previous timeout
        if (usernameCheckTimeout) {
            clearTimeout(usernameCheckTimeout);
        }
        
        // Hide feedback if username is empty
        if (!username) {
            usernameFeedback.style.display = "none";
            return;
        }
        
        // Set a timeout to avoid too many requests while typing
        usernameCheckTimeout = setTimeout(function() {
        fetch(window.checkUsernameUrl ? `${window.checkUsernameUrl}?username=${encodeURIComponent(username)}` : `/users/check-username/?username=${encodeURIComponent(username)}`)
                .then(response => response.json())
                .then(data => {
                    usernameFeedback.style.display = "block";
                    
                    if (data.exists) {
                        usernameFeedback.textContent = "Username already exists";
                        usernameFeedback.className = "text-danger";
                    } else {
                        usernameFeedback.textContent = "Username is available";
                        usernameFeedback.className = "text-success";
                    }
                })
                .catch(error => {
                    console.error("Error checking username:", error);
                    usernameFeedback.style.display = "none";
                });
        }, 500); // Wait 500ms after user stops typing
    });

    // When the user clicks "Register as merchant", the merchant type is automatically selected
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('user_type') === 'merchant') {
        var userTypeField = document.querySelector("input[name='user_type']");
        if (userTypeField) {
            userTypeField.value = 'merchant';
        }
    }
});
