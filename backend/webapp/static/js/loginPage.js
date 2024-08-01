function switchForm(formType) {
    // Hide both forms
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'none';

    // Display the selected form
    document.getElementById(formType + '-form').querySelector('form').reset();
    document.getElementById(formType + '-form').style.display = 'block';

    // Clear error messages
    resetErrorMessages();

    // Change page title accordingly
    document.title = formType === 'login' ? 'Login' : 'Signup';
}




async function handleFormSubmit(event) {
    try {
        event.preventDefault();
        showLoader();
        resetErrorMessages();
        var form = event.target;
        var formData = new FormData(form);
        //for (let [key, value] of formData.entries()) {
        //    console.log(`${key}: ${value}`);
        //}
        if (formData.get('form-type') == 'signup') {
            var passwordFormatStatus = checkPasswordFormat(formData.get('password'));
            if (passwordFormatStatus != 0) {
                document.getElementById('signup-error-' + passwordFormatStatus).style.display = 'block';
                return;
            }
        }
        await sendLoginToServer(formData);
    }
    finally {
        hideLoader();
    }
}


function resetErrorMessages() {
    var errorMessages = document.querySelectorAll('.signup-error-message');
    errorMessages.forEach(element => {
        element.style.display = 'none';
    });

    document.getElementById('login-denied').style.display = 'none';
    document.getElementById('login-wrong-info').style.display = 'none';
}


function checkPasswordFormat(password) {
    // 8 - 20
    if (password.length > 20 || password.length < 8) {
        return 1
    }
    // include one lowercase
    if (!(/[a-z]/.test(password))) {
        return 2
    }
    // include one uppercase
    if (!(/[A-Z]/.test(password))) {
        return 3
    }
    // start with letter
    if (!(/^[a-zA-Z]/.test(password))) {
        return 4
    }
    // digit
    if (!(/\d/.test(password))) {
        return 5
    }
    // special characters
    if (!(/[~!@#$%^&*()\[\]{}\|\\/\-+_=:;<>,.?]/.test(password))) {
        return 6
    }
    // not any other
    if (!(/^[a-zA-Z0-9~!@#$%^&*()\[\]{}\|\\/\-+_=:;<>,.?]+$/.test(password))) {
        return 7
    }
    return 0
}


async function sendLoginToServer(formData) {
    // where to send
    var url = '/login';

    // fetch() request
    var req = {
        method: 'POST',
        body: formData
    };


    // Send the POST request
    //response = await fetch(url, req);
    //console.log('server response');
    //console.log(response);

    //handleLoginResponse(response);
    try {
        response = await fetch(url, req);
        //console.log('server response');
        //console.log(response);
        // Handle the response from the server
        await handleLoginResponse(response);
    } catch (error) {
        console.error('Fetch error:', error);
        alert(`Fetch error: ${error.message}`);
    }

}

async function handleLoginResponse(response) {
    if (response.redirected) {
        var redirectUrl = response.url;
        console.log(redirectUrl)
        if (redirectUrl) {
            window.location.href = redirectUrl;
        } else {
            console.error('not redirecting');
        }
    } else if (response.status == 401 || response.status == 409) {
        console.log('youre wrong');
        respText = await response.text();
        console.log(respText);

        var errorDiv = document.getElementById('login-denied');
        errorDiv.style.display = 'block';
        errorDiv.innerHTML = respText;
        //errorDiv.innerHTML = 'mamma mia!';

        document.getElementById('login-wrong-info').style.display = 'block';
    } else if (response.status == 502) {
        respText = await response.text();
        alert(respText);
    } else {
        console.error('Failed to send request');
    }
}






/*
function getHashedFormData(formData) {
    for (const key in formData) {
        if (Object.hasOwnProperty.call(formData, key)) {
            if (key != 'type') {
                formData[key] = getStringHash(formData[key]);
            }
        }
    }
    return formData
}

function getStringHash(strToHash) {
    //const hash = createHash('md5');
    //hash.update(strToHash);
    //return hash.digest('hex');
    var hash = CryptoJS.MD5("your_string").toString();
    return hash
}


function encryptData(data) {
    // publicKey = {'e':1, 'n':1}
    // (M ^ e) % N
    //var m = getNumericValueStringOfData(data);
    var mArray = new TextEncoder().encode(data);
    //console.log('mArray');
    //console.log(mArray);
    //console.log(mArray);
    //var mArray = divideNumericDataToBlocks(m);
    //var encArray = mArray.map(rsaEncryptDataPiece);
    var encArray = [];
    for (var i = 0; i < mArray.length; i++) {
        encArray.push(rsaEncryptDataPiece(mArray[i]));
    }
    encArray = encArray.map(num => String(num).padStart(10, '0'));
    var encData = encArray.join('');
    //console.log(encArray);
    //console.log('the enc data array: ');
    //console.log(encArray);
    //encArray = encArray.map(block => block.padStart(3, '0'));
    return encData;
}

function rsaEncryptDataPiece(m) {
    //m = parseInt(m);
    var encData = (BigInt(m) ** BigInt(e)) % BigInt(n);
    //console.log(encData);
    //encData = Number(encData);
    //console.log(encData);
    //encData %= publicKey.n;
    //console.log(encData);
    //return String(encData);
    return Number(encData);
}

function rsaDec(c) {
    var d = BigInt(925073);
    var n = BigInt(1942691);
    c = BigInt(c);
    var decData = (c ** d) % n;
    //console.log(Number(decData));
    return Number(decData);
}

function getNumericValueStringOfData(data) {
    // Encode data to a list of ints
    var dataArray = new TextEncoder().encode(data);
    // Convert each integer to a string and pad with '0' to reach a length of 3 characters
    var paddedStrings = dataArray.map(num => String(num).padStart(3, '0'));
    // Join all padded strings into one string
    var joinedString = paddedStrings.join('');
    return joinedString;
}

function divideNumericDataToBlocks(data) {
    var blockLen = 6;
    var blocks = [];
    for (var i = 0; i < data.length; i += blockLen) {
        blocks.push(data.substring(i, i + blockLen));
    }
    return blocks;
}
*/



// on submit check password regex
//send
//recieve ans