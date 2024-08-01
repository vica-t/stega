function addEventListeners() {
    addEventListenersToButtons();
}
document.addEventListener('DOMContentLoaded', addEventListeners)

function addEventListenersToButtons() {
    var forms = document.querySelectorAll('.plan-form');
    forms.forEach(function(forms) {
        forms.addEventListener('submit', handlePlanFormSubmit);
    });
}





async function handlePlanFormSubmit(event) {
    event.preventDefault();
    console.log('clicked button');
    var form = event.target;
    var isActive = form.classList.contains('plan-option');
    if (isActive) {
        var formData = new FormData(form);
        await sendPlanFormToServer(formData);
    }
}


async function sendPlanFormToServer(formData) {
    var url = '/plans';

    var req = {
        method: 'POST',
        body: formData
    };

    try {
        var response = await fetch(url, req);
        //console.log('server response');
        //console.log(response);
        // Handle the response from the server
        await handlePlanResponse(response);
    } catch (error) {
        console.error('Fetch error:', error);
        alert(`Fetch error: ${error.message}`);
    }
}

async function handlePlanResponse(response) {
    console.log('got response')
    if (!response.ok) {
        var respText = await response.text()
        alert(respText);
        return;
    } else if (response.redirected) {
        var redirectUrl = response.url;
        console.log(redirectUrl)
        if (redirectUrl) {
            window.location.href = redirectUrl;
        } else {
            console.error('not redirecting');
        }
    } else {
        console.error('Failed to send request');
    }
}