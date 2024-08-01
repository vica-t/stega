
async function a(event) {
    event.preventDefault();
    console.log('submitted');
    var form = event.target;
    var formData = new FormData(form);
    console.log(formData.get('prompt'));
    console.log(formData.get('style'));
    console.log(formData.get('size'));

    var req = {
        method: 'POST',
        body: formData
    }

    var response = await fetch('/generate-image', req);
    console.log(response);
}



document.getElementById('form').addEventListener('submit', a);


// sk-proj-X4fROlphmIl2O4WWpy9NT3BlbkFJMslQVx21ILEKVkIpZZzW


