
/*
function addEventListeners() {
    document.getElementById('insert-option-button').addEventListener('click', openInsertAction);
    document.getElementById('read-option-button').addEventListener('click', openReadAction);
}
document.addEventListener('DOMContentLoaded', addEventListeners)
*/



async function openInsertAction() {
    await openAction('insert');
}

async function openReadAction() {
    await openAction('read');
}



async function openAction(action) {
    var url = '/' + action;
    var req = {method : 'GET'};
    var response = await fetch(url, req);
    console.log(response);
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



