
function resetSessionTimeout() {
    console.log('session update');
    // Send a request to the server to update the session timeout
    fetch('/update_session_timeout', { method: 'POST' })
        .then(response => {
            if (response.redirected) {
                var redirectUrl = response.url;
                if (redirectUrl) {
                    window.location.href = redirectUrl;
                }
                else {
                    console.error('not redirecting')
                }
            }
            else if (response.ok) {}
            else {
                console.error('not valid request')
            }
        })
        .catch (error => {
            console.error('Error:', error)
        })
}

//function automaticallyLogout() {
//    fetch('/logout', { method: 'POST'});
//}

// Reset session timeout on user interaction events
document.addEventListener('mousedown', resetSessionTimeout);
document.addEventListener('keydown', resetSessionTimeout);
