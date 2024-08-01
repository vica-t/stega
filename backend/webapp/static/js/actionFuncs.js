async function sendActionToServer(formData) {
    actionType = formData.get('form-type');
    var url = '/' + actionType;
    console.log(url);
    var req = {
        method: 'POST',
        body: formData
    };
    console.log('request');
    console.log(req);
    try {
        // Send the POST request
        var firstResponse = await fetch(url, req);
        console.log('got response:', firstResponse);
        // handle response
        await handleActionResponse(firstResponse);
    }
    catch (error) {
        console.error('Fetch error:', error);
        alert(`Fetch error: ${error.message}`);
    }
    
}


function getFetchedFilename(response) {
    try {
        var contentDisposition = response.headers.get('Content-Disposition');
        var match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        var fileName = match[1].replace(/['"]/g, '');
        return fileName;
    }
    catch {
        return null;
    }
}




/*
async function goBackToOptions() {
    var req = {method:'GET'};
    var response = await fetch('/home', req);
    if (response.redirected) {
        var redirectUrl = response.url;
        console.log(redirectUrl)
        if (redirectUrl) {
            window.location.href = redirectUrl;
        }
        else {
            console.error('not redirecting');
            alert('Couldn\'t redirect');
        }
    }
    else {
        var respText = await response.text();
        alert(respText);
        console.log(respText);
    }
}
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('return-to-options-button').addEventListener('click', goBackToOptions);
})
*/


