function addEventListeners() {
    document.getElementById('verification-form').addEventListener('submit', handleCodeSubmit);
}
document.addEventListener('DOMContentLoaded', addEventListeners);


async function handleCodeSubmit(event) {
    event.preventDefault();
    var form = event.target;
    var formData = new FormData(form);

    var req = {
        method: 'POST',
        body: formData
    };

    var response = await fetch('/verify', req);
    console.log(response);
    if (response.redirected) {
        var redirectUrl = response.url;
        if (redirectUrl) {
            window.location.href = redirectUrl;
        } else {
            console.error('not redirecting')
        }
    } else {
        console.error('not valid request')
    }
}