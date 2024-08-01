
async function readMetadata(file) {
    return new Promise((resolve, reject) => {
        var reader = new FileReader();
        reader.onload = async function(e) {
            var metadata = null;
            if(file.type === "image/png") {
                // file is png
                metadata = await readPngMetadata(e);
            } else if (file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {
                // file is docx
                metadata = await readDocxMetadata(e);
            } else {
                // file is some other data type
                reject(new Error('Unaccepted file format.')); // Reject the promise
                return;
            }
            resolve(metadata);
        }
        reader.onerror = function(event) {
            console.log('error in metadata file reader');
            reject(new Error('An error occured, please try again...')); // Reject the promise
        }
        reader.readAsArrayBuffer(file);
    })
}


async function readPngMetadata(e) {
    return new Promise((resolve, reject) => {
        var buffer = e.target.result;
        var view = new DataView(buffer);

        let position = 8;
        while (position < view.byteLength) {
            var length = view.getUint32(position);
            position += 4;
            var type = Array.from(new Uint8Array(buffer, position, 4)).map(byte => String.fromCharCode(byte)).join('');
            position += 4;
            if (type === 'tEXt') {
                var data  = Array.from(new Uint8Array(buffer, position, length)).map(byte => String.fromCharCode(byte)).join('');
                if (data.slice(0,10) == 'identifier') {
                    var identifier = data.slice(11);
                    console.log('identifier: ' + identifier);
                    resolve(identifier); // Resolve the promise
                    return;
                }
            }
            position += length + 4;
        }
        resolve(); // Resolve the promise even if no identifier is found
    });
}















