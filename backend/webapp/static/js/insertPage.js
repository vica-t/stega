function addEventListeners() {
    document.getElementById('insert-action-form').addEventListener('submit', handleInsertFormSubmit);
    document.getElementById('generate-image-button').addEventListener('click', generateImage);
}
document.addEventListener('DOMContentLoaded', addEventListeners)








async function handleInsertFormSubmit(event) {
    try {
        event.preventDefault();
        //console.log('inserting');

        showLoader();
        disableSubmitButtons();

        var form = event.target;
        var formData = new FormData(form);

        if (!(await validateInsertForm(formData))) {
            return;
        }

        await sendActionToServer(formData);
    } finally {
        enableSubmitButtons();
        hideLoader();
    }
}

async function validateInsertForm(formData) {
    var dataInput = formData.get('data-textarea');
    var dataFile = formData.get('data-file');
    console.log(dataInput);
    console.log(dataFile);
    if ((dataInput && dataFile.name) || (!dataInput && !dataFile.name)) {
        alert('Please provide data to insert in one of the fields.');
        return false;
    }

    var mediumFile = formData.get('medium-file');
    var generatedImage = document.getElementById('generated-image-preview');
    console.log(mediumFile);
    console.log(generatedImage);
    if ((generatedImage && mediumFile.name) || (!generatedImage && !mediumFile.name)) {
        alert('Please provide a file to insert data into in one of the fields.');
        return false;
    }
    return true;
}



async function handleActionResponse(response) {
    console.log('handling respone');

    var req = { method: 'GET' };
    var secondResponse = await fetch('/insert-plan-info', req);

    if (!secondResponse.ok) {
        var respText = await secondResponse.text();
        alert(respText);
        console.error(respText);
        return;
    }
    if (!response.ok) {
        var respText = await response.text();
        alert(respText);
        console.error(respText);
        return;
    }

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

    var planInfo = await secondResponse.json();
    var insertForm = document.getElementById('insert-action-form');
    insertForm.id = insertForm.id + planInfo.actionFormIdAddon;
    document.getElementById('plan-info-block').innerHTML = planInfo.planInfoBlockContent;
    //{
    //    'actionFormIdAddon' : actionFormIdAddon,
    //    'planInfoBlockContent' : planInfoBlockContent
    //}
}






async function generateImage(event) {
    try {
        showLoader();
        disableSubmitButtons();

        clearGeneratedImage();
        var prompt = document.getElementById('prompt').value;
        var style = document.querySelector('input[name="style"]:checked').value;
        var size = document.querySelector('input[name="size"]:checked').value;

        if (prompt.trim() == '') {
            alert('Please write a description of a picture you want to generate.');
            return;
        }

        var req = {
            method: 'POST',
            body: new URLSearchParams({ prompt, style, size })
        };

        var response = await fetch('/generate-image', req);
        var imageContainer = document.getElementById('image-container');
        if (!response.ok) {
            var respText = await response.text();
            imageContainer.innerHTML = `
                <p>${respText} try again...</p>
            `;
            return;
        }
        var data = await response.json();
        var generatedImageInput = document.getElementById('generated-image');
        var b64Image = data.data[0].b64_json;
        imageContainer.innerHTML = `
            <img src="data:image/png;base64,${b64Image}" alt="Generated Image" width=30% id="generated-image-preview">
            <br>
            <button type="button" id="clear-image-button">Clear image</button>
        `;
        generatedImageInput.value = b64Image;

        document.getElementById('clear-image-button').addEventListener('click', clearGeneratedImage);
    } finally {
        enableSubmitButtons();
        hideLoader();
    }

}

function clearGeneratedImage() {
    document.getElementById('image-container').innerHTML = '';
    document.getElementById('generated-image').value = '';
}







function disableSubmitButtons() {
    document.getElementById('submit-insert-data').disabled = true;
    document.getElementById('generate-image-button').disabled = true;
}

function enableSubmitButtons() {
    document.getElementById('submit-insert-data').disabled = false;
    document.getElementById('generate-image-button').disabled = false;
}