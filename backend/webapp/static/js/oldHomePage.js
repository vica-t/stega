/*
//console.clear()
// Generate the key
window.crypto.subtle.generateKey(
    {
        name: 'AES-GCM', // Algorithm name (e.g., AES-GCM)
        length: 256,     // Key length in bits
    },
    true,              // Whether the key is extractable
    ['encrypt', 'decrypt'] // Key usage
)
.then((key) => {
    // Save the key to localStorage
    window.localStorage.setItem('key', JSON.stringify(key));
    console.log('Saved key', key, 'to local storage')
})
// send to server
.catch((error) => {
    console.error('Key generation error:', error);
});

// Later, on another page:
// Retrieve the key from localStorage
//const storedKey = JSON.parse(window.localStorage.getItem('key'));
//*/






function addEventListeners() {
    document.getElementById('return-to-options-button').addEventListener('click', goBackToOptions);
    document.getElementById('insert-option-button').addEventListener('click', openInsertAction);
    document.getElementById('read-option-button').addEventListener('click', openReadAction);
    document.getElementById('insert-action-form').addEventListener('submit', handleInsertFormSubmit);
    document.getElementById('read-action-form').addEventListener('submit', handleReadFormSubmit);
}
document.addEventListener('DOMContentLoaded', addEventListeners)





function goBackToOptions() {
    var actionsBlock = document.getElementById('actions-block');
    var optionsBlock = document.getElementById('options-block');
    actionsBlock.style.display = 'none';
    optionsBlock.style.display = 'block';
    //console.log('switching to form');
    //console.log('changing button');
    //b = document.getElementById('insert-button');
    //console.log(b);
    //b.style.display = 'none';
    //console.log('changing form');
    //f = document.getElementById('insert-form');
    //console.log(f);
    //f.style.display = 'block';
}

function openInsertAction() {
    goToActions()
    var actionsBlocks = getActionsBlocks();
    var insertBlock = actionsBlocks[0];
    var readBlock = actionsBlocks[1];
    insertBlock.style.display = 'block';
    readBlock.style.display = 'none';
}

function openReadAction() {
    goToActions()
    var actionsBlocks = getActionsBlocks();
    var insertBlock = actionsBlocks[0];
    var readBlock = actionsBlocks[1];
    insertBlock.style.display = 'none';
    readBlock.style.display = 'block';
}

function goToActions() {
    var actionsBlock = document.getElementById('actions-block');
    var optionsBlock = document.getElementById('options-block');
    actionsBlock.style.display = 'block';
    optionsBlock.style.display = 'none';
}

function getActionsBlocks() {
    resetActionForms()
    var insertBlock = document.getElementById('insert-action-block');
    var readBlock = document.getElementById('read-action-block');
    return [insertBlock, readBlock];
}

function resetActionForms() {
    document.getElementById('insert-action-form').reset();
    document.getElementById('read-action-form').reset();
    var downloadLink = document.getElementById('download-link');
    downloadLink.href = "";
    downloadLink.download = "";
    downloadLink.style.display = 'none';
    downloadLink.textContent = '';
}





async function handleInsertFormSubmit(event) {
    event.preventDefault();
    console.log('inserting');

    var form = event.target;
    var formData = new FormData(form);

    if (!validateInsertForm()) {
        return;
    }

    await sendActionToServer(formData);
}

function validateInsertForm() {
    var dataInput = document.getElementById('data-textarea').value;
    var dataFile = document.getElementById('data-file').files;
    if ((dataInput && dataFile.length) || (!dataInput && !dataFile.length)) {
        alert('Please provide data to insert in only one of the fields.');
        return false;
    }
    var mediumFile = document.getElementById('medium-file').files;
    if (mediumFile.length == 0) {
        alert('Please provide file to inset data into.');
        return false;
    }
    if (dataFile.length > 1 || mediumFile.length > 1) {
        alert('Only one file can be uploaded per field.');
        return false;
    }
    return true;
}



async function handleReadFormSubmit(event) {
    event.preventDefault();
    console.log('reading');

    var form = event.target;
    var formData = new FormData(form);

    await updateReadFormData(formData);

    await sendActionToServer(formData);
}

async function updateReadFormData(formData) {
    modFile = document.getElementById('modified-file').files[0];
    var metadata = await readMetadata(modFile);
    formData.append('metadata', metadata);
}


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
        response = await fetch(url, req);
        console.log('got response:', response);
        // handle response
        await handleActionResponse(response);
    }
    catch (error) {
        console.error('Fetch error:', error);
        alert(`Fetch error: ${error.message}`);
    }
    
}


async function handleActionResponse(response) {
    console.log('handling respone');
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
    downloadLinkObj.textContent = 'Click here to download ready file';
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
async function encryptFormData(formData, aesKey) {
    // Convert FormData to JSON string
    var formDataJson = JSON.stringify([...formData.entries()]);
    // Encrypt FormData JSON string and checksum with AES key
    var encryptedData = await crypto.subtle.encrypt(
        { name: 'AES-GCM', iv: crypto.getRandomValues(new Uint8Array(12)) },
        aesKey,
        new TextEncoder().encode(formDataJson)
    );
    return encryptedData;
}
//*/













// do all the shits and stuff for the page here

//function switchToForm() {
    //    console.log('switching to form');
    //    console.log('changing button');
    //    b = document.getElementById('insert-button');
    //    console.log(b);
    //    b.style.display = 'none';
    //    console.log('changing form')
    //    f = document.getElementById('insert-form');
    //    console.log(f);
    //    f.style.display = 'block';
    //}
    //document.getElementById('insert-button').addEventListener('click', switchToForm);
