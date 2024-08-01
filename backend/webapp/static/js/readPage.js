function addEventListeners() {
    document.getElementById('read-action-form').addEventListener('submit', handleReadFormSubmit);
}
document.addEventListener('DOMContentLoaded', addEventListeners)





async function handleReadFormSubmit(event) {
    try {
        event.preventDefault();
        //console.log('reading');

        showLoader();
        disableButton();

        var form = event.target;
        var formData = new FormData(form);

        await updateReadFormData(formData);

        await sendActionToServer(formData);
    } finally {
        enableButton();
        hideLoader();
    }

}

async function updateReadFormData(formData) {
    modFile = document.getElementById('modified-file').files[0];
    var metadata = await readMetadata(modFile);
    formData.append('metadata', metadata);
}



async function handleActionResponse(response) {
    console.log('handling respone');
    var blob = await response.blob();
    var fileName = getFetchedFilename(response);
    if (fileName == null) {
        alert('Something went wrong');
        console.error('Couldn\'t read file name');
        return;
    }
    var downloadLinkObj = document.getElementById('download-link');
    var url = URL.createObjectURL(blob);
    downloadLinkObj.href = url;
    downloadLinkObj.download = fileName;
    downloadLinkObj.style.display = 'block';
    downloadLinkObj.textContent = 'Your file is ready. Click here to download.';
}



function disableButton() {
    document.getElementById('submit-read-data').disabled = true;
}

function enableButton() {
    document.getElementById('submit-read-data').disabled = false;
}