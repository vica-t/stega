import tracemalloc
tracemalloc.start()

import os
import sys
sys.path.append(os.path.abspath(''))

from quart import Quart, render_template, session, request, redirect, send_file, abort, jsonify
import httpx
import base64
import shutil
import hashlib
import random
import threading
import werkzeug
import time
import random
import aiofiles
from backend.functionality import Waiter, ImageMetadataHandler













app = Quart(__name__)
#app.config['SESSION_TYPE'] = 'filesystem'  # You can change this to other session types as needed
#Session(app)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_HTTPONLY'] = True    # prevent client side javascript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'


def generateSessionSecretKey():
    """
    Generates a session secret key.

    :return: The generated session secret key.
    """
    now = time.time()
    randInt = random.randint(0, 1000000)
    key = str(now) + str(randInt)
    key = getSha256Hash(key)
    return key

def getSha256Hash(strToHash):
    """
    Calculates the SHA-256 hash of the given string.

    :param strToHash: The string to be hashed.
    :type strToHash: str
    :return: The SHA-256 hash of the string.
    :rtype: str
    """
    bytesToHash = strToHash.encode('utf-8')
    hashObj = hashlib.sha256()
    hashObj.update(bytesToHash)
    shaObj = hashObj.hexdigest()
    return shaObj

app.secret_key = generateSessionSecretKey()
#app.config['PERMANENT_SESSION_LIFETIME'] = 3600 # session timeout 1 hour





##KEY_GENERATOR = KeyGenerator()
WAITER = Waiter()
IMAGE_METADATA_HANDLER = ImageMetadataHandler()
OPENAI_API_KEY = 'sk-proj-X4fROlphmIl2O4WWpy9NT3BlbkFJMslQVx21ILEKVkIpZZzW'
ALLOWED_FORMATS = {'jpg', 'jpeg', 'png', 'gif', 'txt', 'pdf', 'docx', 'xlsx', 'pptx', 'bmp', 'mp3', 'wav', 'mp4', 'mov', 'csv', 'json', 'rtf', 'epub', 'zip'}

def emptyUploadFolder():
    """
    Remove all files and folders in the upload folder.

    :return: None
    """
    for filename in os.listdir(UPLOAD_FOLDER_PATH):
        filePath = os.path.join(UPLOAD_FOLDER_PATH, filename)
        try:
            if os.path.isfile(filePath) or os.path.islink(filePath):
                os.unlink(filePath)  # remove the file or link
            elif os.path.isdir(filePath):
                shutil.rmtree(filePath)  # remove the directory and all its contents
        except Exception as e:
            print('Failed to delete ' + filePath)
            print(e)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER_PATH = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER_PATH, exist_ok=True)
emptyUploadFolder()




# script fetching

@app.route('/static/js/homePage.js', methods=['GET'])
async def getHomePageScript():
    """
    Returns the home page script file if the referrer starts with the URL root and the session contains the 'username' key.
    Otherwise, aborts the request with 401 status code.

    :return: None
    """
    if (request.referrer and request.referrer.startswith(request.url_root)) and 'username' in session:
        scriptPath = os.path.join(BASE_DIR, 'static', 'js', 'homePage.js')
        return await send_file(scriptPath, as_attachment=True)
    return abort(401)

@app.route('/static/js/plansPage.js', methods=['GET'])
async def getPlansPageScript():
    """
    Retrieves the plansPage.js script file and sends it as a response.

    :return: The plansPage.js script file as an attachment if the request is valid and the user is authenticated. Returns a 401 error if the request is not valid or the user is not authenticated.

    """
    if (request.referrer and request.referrer.startswith(request.url_root)) and 'username' in session:
        scriptPath = os.path.join(BASE_DIR, 'static', 'js', 'plansPage.js')
        return await send_file(scriptPath, as_attachment=True)
    return abort(401)


@app.route('/static/<path:filename>', methods=['GET'])
async def customStatic(filename):
    """
    Serve static files from the 'static' folder.

    :param filename: The filename of the static file to be served.
    :return: The static file as an attachment, or an appropriate error response.

    """
    if not (request.referrer and request.referrer.startswith(request.url_root)):
        return abort(403)  # Forbidden
    staticFolder = os.path.join(app.root_path, 'static')
    filePath = os.path.join(staticFolder, filename)
    if os.path.isfile(filePath):
        return await send_file(filePath, as_attachment=True)
    else:
        return abort(404)  # Not Found




@app.route('/fpl', methods=['GET'])
async def forgotPasswordLink():
    ##print('forgotPasswordLink')
    ##userHash = request.args.get('h')
    ##print(userHash)
    # check if changePass exists in db
    ##if not await WAITER.runTask('validChangePassUser', {'userHash':userHash}):
    ##    return abort(401)
    ##session['changePass'] = userHash
    ##print('added changePass: ' + session['changePass'])
    session['name'] = 'vasya'
    ##print(session['name'])
    return redirect('/b')



@app.route('/change-password', methods=['GET'])
async def renderChangePasswordPage():
    print('found!')
    #print(session['name'])
    session['test1'] = 'TEST1'
    print(session['test1'])
    if 'changePass' not in session:
        print('changePass not in session')
        return abort(404)
    userHash = session['changePass']
    # check if changePass exists in db
    if not await WAITER.runTask('validChangePassUser', {'userHash':userHash}):
        return abort(401)
    cache_buster = str(time.time())
    return await render_template('changePassword.html', cache_buster=cache_buster)

@app.route('/change-password', methods=['POST'])
async def handleChangePasswordFormSubmit(request):
    if 'changePass' not in session:
        return abort(404)
    userHash = session['changePass']
    if not await WAITER.runTask('validChangePassUser', {'userHash':userHash}):
        return abort(401)
    form = await request.form
    password = form.get('password')
    confirmPassword = form.get('confirm-password')
    result = await WAITER.runTask('changePassword', {'userHash':userHash, 'password':password, 'confirmPassword':confirmPassword})
    if not result:
        return 'Couldn\'t change password', 502
    session.pop('changePass')
    return redirect('/login')




@app.route('/<reqUrl>', methods=['GET'])
async def parseGetURL(reqUrl):
    """
    Retrieves the GET URL and processes it.

    :param reqUrl: The requested URL.
    :return: The processed URL.
    """
    print(f'-{reqUrl}-')
    publicPages = {'':index, 'login':generateLoginPage, 'logout':logout, 'forgot-password':generateForgotPasswordPage, 'about':generateAboutPage, 'how-to-use':generateHowToPage}
    privatePages = {'home':generateHomePage, 'insert':generateInsertPage, 'read':generateReadPage, 'plans':generatePlansPage, 'insert-plan-info':handleGetInsertPlanInfo, 'verify':generateVerifyPage, 'resend-email':resendEmail}
    return await processURL(request, reqUrl, publicPages, privatePages)

@app.route('/<reqUrl>', methods=['POST'])
async def parsePostURL(reqUrl):
    """
    :param reqUrl: The requested URL.
    :return: The result of processing the URL.
    """
    # insert read generate-image  plans
    publicPosts = {'login':authenticateUser, 'update_session_timeout':updateSessionTimeoutOnActivity, 'forgot-password':handleForgotPasswordFormSubmit}
    privatePosts = {'insert':handleInsert, 'read':handleRead, 'generate-image':handleGenerateImage, 'plans':handlePlanFormSubmit, 'verify':handleVerifySubmit}
    return await processURL(request, reqUrl, publicPosts, privatePosts)


async def processURL(request, reqUrl, publicDict, privateDict):
    """
    Process a URL request and determine the action to perform based on the URL parameters and dictionaries provided.

    :param request: The request object, containing information about the HTTP request.
    :param reqUrl: The URL string to process.
    :param publicDict: A dictionary containing public URLs and their associated actions.
    :param privateDict: A dictionary containing private URLs and their associated actions.
    :return: The result of the URL processing, which could be a redirected response or an HTTP error code (404).
    """
    reqUrl = reqUrl.lower()

    if reqUrl in list(publicDict.keys()):
        return await processPublicPage(request, publicDict[reqUrl])
    elif reqUrl in list(privateDict.keys()):
        return await processPrivatePage(request, reqUrl, privateDict[reqUrl])
    else:
        return abort(404)

async def processPublicPage(request, func):
    """
    :param request: The request object containing information about the HTTP request.
    :param func: The function that will be executed with the request object.
    :return: The result of executing the given function with the request object.
    """
    return await func(request)

async def processPrivatePage(request, reqUrl, func):
    """
    Process private page.

    :param request: the request object.
    :param reqUrl: the requested URL.
    :param func: the function to be executed.
    :return: the result of the executed function.
    """
    print('- processing private page')
    if 'username' in session:
        print('username in session')
        if reqUrl in ['verify', 'plans']:
            print('req is verify or plans')
            return await func(request)
        if 'verified' in session:
            print('verified in session')
            if 'plan' in session:
                print('plan in session')
                return await func(request)
            print('redirecting to plans')
            return redirect('/plans')
        print('redirecting to verify')
        return redirect('/verify')
    print('redirecting to login')
    return redirect('/login')




# Route to serve the HTML page
async def index(request):
    """
    :param request: The request object representing the HTTP request.
    :return: Returns a redirect response to the "/home" URL.
    """
    return redirect('/home')

async def generateAboutPage(request):
    cache_buster = str(time.time())
    return await render_template('about.html', cache_buster=cache_buster)

async def generateHowToPage(request):
    cache_buster = str(time.time())
    return await render_template('how-to-use.html', cache_buster=cache_buster)

    
async def generateLoginPage(request):
    """
    Generate the login page.

    :param request: The request object.
    :return: The generated login page as a response.
    """
    if 'username' in session:
        return redirect('/home')

    ##keys = KEY_GENERATOR.generateKeys()
    #publicKey = keys['public']
    #session['privateKey'] = keys['private']
    cache_buster = str(time.time())
    return await render_template('login.html', cache_buster=cache_buster)
    

async def authenticateUser(request):
    """
    Authenticates a user based on the provided request.

    :param request: The user's request.
    :return: A tuple containing the response and status code.
    """
    # get req that is headers etc and body is json stringify of formData
    # formData is type, username, password, ?confirmPassword
    # get, decode, jsonify, runTask, return
    # runTask: check valid task, encode, send to appropriate client, get response, return
    # client: recieves task, check valid task, handle, encode response, return

    formType, data = await getLoginRequestData(request)
    if not formType:
        return '', 400
    #success, usernameHash = await WAITER.runTask(formType, data)
    #success, usernameHash = await asyncio.to_thread(WAITER.runTask, formType, data)
    result = await WAITER.runTask(formType, data)

    if result == None:
        print('result is none')
        return deniedLogin(formType)
    elif result == False:
        return 'Server encountered an error, try again later...', 502
    success, usernameHash, verified, currentPlan = result
    if success:
        startSession(usernameHash)
        if not verified:
            return redirect('/verify')
        session['verified'] = True
        if not currentPlan:
            return redirect('/plans')
        session['plan'] = currentPlan
        return redirect('/home')
    print('other')
    return deniedLogin(formType)


async def getLoginRequestData(request):
    """
    :param request: An HTTP request object.
    :return: A tuple containing the form type and the data.

    This method takes an HTTP request object as input and extracts the login data from it. It returns a tuple containing the form type and the extracted data. If the form type is not 'login' or 'signup', it returns None, None. If any exception occurs during the extraction process, it also returns None, None.
    """
    try:
        form = await request.form
        data = {}
        formType = form.get('form-type')
        if formType not in ['login', 'signup']:
            return None, None
        data['username'] = form.get('username')
        data['password'] = form.get('password')
        if formType == 'signup':
            data['confirmPassword'] = form.get('confirm-password')
        return formType, data
    except:
        return None, None

def deniedLogin(reqType):
    """
    Returns a tuple containing an error message and the corresponding HTTP status code.

    :param reqType: A string indicating the type of request. Possible values: 'login', 'signup'.
    :type reqType: str
    :return: A tuple containing an error message and the corresponding HTTP status code.
    :rtype: tuple[str, int]
    """
    if reqType == 'login':
        return 'Wrong email or password', 401
    elif reqType == 'signup':
        return 'Email already loggen in to the system', 409
    return abort(401)

def startSession(username):
    """
    Start a new session for the given username.

    :param username: The username of the user.
    :type username: str
    :return: None
    :rtype: None
    """
    session['username'] = username



async def generateVerifyPage(request):
    if 'sentVer' not in session:
        session['sentVer'] = True
        await sendVerificationEmail()
    cache_buster = str(time.time())
    return await render_template('verify.html', cache_buster=cache_buster)

async def resendEmail(request):
    await sendVerificationEmail()

async def sendVerificationEmail():
    await WAITER.runTask('sendVerificationEmail', {'userHash':session['username']})


async def handleVerifySubmit(request):
    form = await request.form
    code = form.get('code-input')
    code = str(code).zfill(6)
    data = {'userHash':session['username'], 'code':code}
    verified = await WAITER.runTask('verifyEmail', data)
    if verified:
        session['verified'] = True
        return redirect('/home')
    return 'Wrong verification code', 401



# GET /forgotPassword
async def generateForgotPasswordPage(request):
    # if user is not logged in he can do forgot password and get redirected here
    # so no session still
    # generate page
    cache_buster = str(time.time())
    return await render_template('forgotPassword.html', cache_buster=cache_buster)


# POST /forgotPassword
async def handleForgotPasswordFormSubmit(request):
    # get the form
    form = await request.form
    # get the email from the form
    email = form.get('email')
    result = await WAITER.runTask('forgotPassword', {'email':email})
    if result == None:
        return 'No existing account for the email you provided', 401
    if not result:
        return 'Server encountered an error, try again later...', 502
    return '', 200
    # when a link like this is entered check if the username is in the table
    # if no say sorry lol
    # if yes redirect to change password page
    # change password page is new password and confirm password
    # submitted check if username in table
    # check if new password is the same as prev
    # change and redirect to login page




async def generateHomePage(request):
    """
    Generate the home page.

    :param request: the request object
    :return: the rendered home page as a string
    """
    cache_buster = str(time.time())
    return await render_template('home.html', cache_buster=cache_buster)



async def generateInsertPage(request):
    """
    Generate the insert page.

    :param request: The request object.
    :return: The rendered insert page.
    """
    cache_buster = str(time.time())
    result = await getPlanInfoForInsertPage()

    if result == None:
        return abort(500)
    actionFormIdAddon, planInfoBlockContent = result

    return await render_template('insert.html', cache_buster=cache_buster, action_form_id_addon=actionFormIdAddon, plan_info_block_content=planInfoBlockContent)

async def getPlanInfoForInsertPage():
    """
    Get plan information for the insert page.

    :return: A tuple containing the action form ID addon and the plan info block content.
    """
    result = await WAITER.runTask('getCreationsLeft', {'userHash':session['username']})

    if (result == False and isinstance(result, bool)) or result == None:
        return None

    actionFormIdAddon = ''
    if result == 0:
        actionFormIdAddon = '-inactive'
        planInfoBlockContent = '''
            <p>You're all out of files to create for today! :(</p><br>
            <a href="/plans">Upgrade your plan?</a>
        '''
    elif result == -1:
        planInfoBlockContent = '''
            <p>You can create an unlimited amount of files!</p><br>
            <script>
                document.getElementById('insert-action-form').addEventListener('submit', handleInsertFormSubmit);
            </script>
        '''
    else:
        planInfoBlockContent = f'''
            <p>You have {result} files to create left for today!</p><br>
            <script>
                document.getElementById('insert-action-form').addEventListener('submit', handleInsertFormSubmit);
            </script>
        '''
    return actionFormIdAddon, planInfoBlockContent



async def handleInsert(request):
    """
    Handles the insertion of data into the server.

    :param request: The request object containing the data to be inserted.
    :return: The result of the insertion process.
    """

    requestData = await getInsertRequestData(request)

    if isinstance(requestData, int):
        return handleInsertError(requestData)
    result = await WAITER.runTask('insert', requestData)

    if not result:
        return 'Server encountered an error, try again later...', 502
    elif result == -1:
        # file not big enough
        return 'The provided file is not big enough to complete task.', 502
    return await handleInsertResult(result)


async def getInsertRequestData(request):
    """
    :param request: The HTTP request object.
    :return: The request data dictionary containing the user hash, form type, received data, medium file, and intended users list.

    """
    try:
        form = await request.form
        files = await request.files
        data = {'userHash':session['username']}
        formType = form.get('form-type')
        if formType != 'insert':
            return 0
        # data-textarea, data-file
        # medium-file
        # intended-user012
        errorGettingReceivedData = await appendReceivedDataToRequestData(form, files, data)
        if errorGettingReceivedData is not None:
            return errorGettingReceivedData # 0-failed, 1-wrongly filled data
        errorGettingMediumFile = await appendReceivedMediumFileToRequestData(form, files, data)
        if errorGettingMediumFile is not None:
            return errorGettingMediumFile # 0-failed, 2-wrongly filled medium file, 3-medium file type not allowed
        errorGettingIntendedUsersList = await appendIntendedUsersListToRequestData(form, data)
        if errorGettingIntendedUsersList is not None:
            return errorGettingIntendedUsersList # 0-failed, 2-wrongly filled intended users
        return data
    except Exception as e:
        print('returning 400')
        print(e)
        return 0 # failed


async def appendReceivedDataToRequestData(form, files, data):
    """
    :param form: A dictionary containing data received from a form submission.
    :param files: A dictionary containing files received from a form submission.
    :param data: A dictionary containing data to be appended with the received data.
    :return: An integer representing the error status. A value of -1 indicates success, while values greater than or equal to 0 indicate errors.

    This method appends the received data to the existing data dictionary. It performs the following steps:
    1. Retrieves the 'data-textarea' value from the form dictionary.
    2. Retrieves the 'data-file' value from the files dictionary.
    3. Checks if either the data or data file is empty.
    4. Determines the file type and retrieves the file data if necessary.
    5. Updates the data dictionary with the data file and file type.
    6. Returns the error status.

    If an error occurs during the process, the error status is set to 0. The method attempts the process twice before returning the error status.
    """
    errorStatus = -2
    for _ in range(2):
        if errorStatus != -1:
            try:
                insertedData = form.get('data-textarea')
                insertedDataFile = files.get('data-file')
                dataEmpty = not insertedData or insertedData.strip() == ''
                dataFileEmpty = insertedDataFile is None or insertedDataFile.filename == ''

                if dataEmpty ^ dataFileEmpty:
                    dataFile, fileType = await getReceivedDataFile(insertedData if dataFileEmpty else insertedDataFile)
                    if not dataFile:
                        errorStatus = 0
                else:
                    errorStatus = 1 # wrongly filled in data
                if errorStatus < 0:
                    data['dataFile'] = dataFile
                    data['dataFileType'] = fileType
                    errorStatus = -1
            except Exception as e:
                print('failed doing append received data')
                print(e)
                errorStatus = 0
    if errorStatus >= 0:
        return errorStatus

async def getReceivedDataFile(receivedData):
    """
    :param receivedData: The data or file to be saved. The receivedData parameter can either be a string or a FileStorage object.
    :return: A tuple containing the bytes of the saved file and the file extension. If an error occurs during saving or reading the file, None will be returned for both values.

    """
    if isinstance(receivedData, str):
        filePath = getFilePathToSave('.txt')
        async with aiofiles.open(filePath, 'w') as f:
            await f.write(receivedData)
    elif isinstance(receivedData, werkzeug.datastructures.FileStorage):
        filePath = getFilePathToSave(receivedData.filename)
        await receivedData.save(filePath)
    else:
        return None, None
    # read bytes from file path
    try:
        async with aiofiles.open(filePath, 'rb') as f:
            byteFile = await f.read()
        deleteFile(filePath, False)
        return byteFile, filePath.split('.')[-1]
    except Exception as e:
        print('after saving data couldnt read it again')
        print(e)
        return None, None

def getFilePathToSave(fileName):
    """
    :param fileName: a string representing the name of the file to be saved
    :return: a string representing the file path where the file will be saved
    """
    newFileName = str(time.time()).replace('.', '') + str(random.randint(0,10000)) + fileName
    newFilePath = os.path.join(UPLOAD_FOLDER_PATH, newFileName)
    return newFilePath


async def appendReceivedMediumFileToRequestData(form, files, data):
    """
    :param form: The request form data.
    :param files: The received files from the request.
    :param data: The request data dictionary.
    :return: Returns an integer indicating the error status. (0 or greater for error, -1 for success)

    The `appendReceivedMediumFileToRequestData` method appends the received medium file to the request data provided. It checks if the medium file or the generated image file is present, and appends the appropriate file to the request data. If both the medium file and the generated image file are present, it returns an error status of 2.

    If the operation fails, it returns an error status of 0. Otherwise, it returns -1 indicating success.

    Note: This method is an asynchronous function.
    """
    errorStatus = -2
    for _ in range(2):
        if errorStatus != -1:
            try:
                mediumFile = files.get('medium-file')
                generatedImage = form.get('generated-image')
                mediumFileEmpty = mediumFile is None or mediumFile.filename == ''
                generatedImageEmpty = generatedImage is None or generatedImage == ''

                if mediumFileEmpty ^ generatedImageEmpty:
                    mediumFile = mediumFile if generatedImageEmpty else generatedImage
                    result = await getReceivedMediumFile(mediumFile, 'medium' if generatedImageEmpty else 'generated')
                    if result == None:
                        errorStatus = 0
                    elif result == False:
                        errorStatus = 3
                    else:
                        mediumFile, mediumFileType = result
                else:
                    errorStatus = 2 # wrongly filled in medium file
                if errorStatus < 0:
                    data['mediumFile'] = mediumFile
                    data['mediumFileType'] = mediumFileType
                    errorStatus = -1
            except Exception as e:
                print('failed doing append received medium file')
                print(e)
                errorStatus = 0
    if errorStatus >= 0:
        return errorStatus

async def getReceivedMediumFile(receivedFile, fileType):
    """
    :param receivedFile: The file or content to be processed.
    :param fileType: The type of file to determine the processing logic. Possible values are 'generated' or 'medium'.
    :return: A tuple containing the processed file data and its file extension if successful, otherwise None.

    This method is used to process received medium files. Depending on the fileType parameter, the method performs different operations on the receivedFile.

    If the fileType is 'generated', the receivedFile is interpreted as base64 encoded image data. The method decodes the data, saves it to a file with a '.png' extension, and returns the processed file data and file extension.

    If the fileType is 'medium', the receivedFile is expected to be a file object. The method saves the file to a designated file path and returns the processed file data and file extension.

    If the fileType does not match any of the expected values, None is returned.

    Note: This method uses asynchronous operations and requires the aiofiles library to be installed.
    """
    try:
        if fileType == 'generated':
            filePath = getFilePathToSave('.png')
            receivedFile = base64.b64decode(receivedFile)
            # Save the image to a file or handle it as needed
            async with aiofiles.open(filePath, 'wb') as imageFile:
                await imageFile.write(receivedFile)
        elif fileType == 'medium':
            filePath = getFilePathToSave(receivedFile.filename)
            if filePath.split('.')[-1] not in ALLOWED_FORMATS:
                return False
            await receivedFile.save(filePath)

        else:
            return None
    except Exception as e:
        print(e)
        return None
    try:
        async with aiofiles.open(filePath, 'rb') as f:
            byteFile = await f.read()
        deleteFile(filePath, False)
        return byteFile, filePath.split('.')[-1]
    except Exception as e:
        print(e)
        return None


async def appendIntendedUsersListToRequestData(form, data):
    """
    :param form: A dictionary containing the form data.
    :param data: A dictionary to which the intended users list will be appended.
    :return: An integer indicating the error status. If the value is negative, it indicates that there was no error. Otherwise, it indicates the error status code.

    This method appends the intended users list to the `data` dictionary. The intended users list is obtained from the `form` dictionary by iterating over the keys 'intended-user0', 'intended-user1', and 'intended-user2'. If any of these keys exist and their corresponding values are non-empty strings, they are added to the list. Duplicate users are removed from the list before it is appended to the `data` dictionary.

    If the length of the intended users list is 0, the error status will be set to 3. If an exception occurs while retrieving the user list, the error status will be set to 0. If there is no error, the list is appended to the `data` dictionary with the key 'intendedUsersList'.

    The error status is returned at the end of the method.
    """
    errorStatus = -2
    for _ in range(2):
        if errorStatus != -1:
            try:
                intendedUsersList = [form.get('intended-user' + str(i)) for i in range(3)]
                intendedUsersList = [user for user in intendedUsersList if user and user.strip()]
                intendedUsersList = list(set(intendedUsersList))
                if len(intendedUsersList) == 0:
                    errorStatus = 4
                if errorStatus < 0:
                    data['intendedUsersList'] = intendedUsersList
                    errorStatus = -1
            except:
                print('couldnt get user list')
                errorStatus = 0
    if errorStatus >= 0:
        return errorStatus


def handleInsertError(errorCode):
    """
    Handles the error that occurs during an insert operation.

    :param errorCode: The error code indicating the specific error that occurred.
    :return: A tuple containing the error message and the status code.
    """
    if errorCode == 0:
        # failed
        return '', 400
    if errorCode == 1:
        # wrongly filled data
        return 'Provide one file of data or type in data to proceed.', 400
    if errorCode == 2:
        # wrongly filled medium file
        return 'Provide a single file to insert data into to proceed.', 400
    if errorCode == 3:
        return 'Provided file format is not allowed.', 400
    if errorCode == 4:
        # wrongly filled intended users
        return 'Provide between one and three users to proceed.', 400


async def handleInsertResult(result):
    """
    Handles the result of an insert operation.

    :param result: A tuple containing the file bytes, file type, and metadata.
    :return: If successful, returns the file path to the saved file as an attachment. If an error occurs, returns a message indicating a server error.

    """
    # save file bytes to some name with type and insert metadata
    fileBytes, metadata = result
    filePath = getFilePathToSave( '.png')
    try:
        async with aiofiles.open(filePath, 'wb') as f:
            await f.write(fileBytes)
        resultStatus = None
        for _ in range(2):
            if resultStatus != 1:
                resultStatus = IMAGE_METADATA_HANDLER.addMetadata(filePath, metadata)
        if resultStatus != 1:
            return 'Server encountered an error, try again later...', 502
        
        deletionThread = threading.Thread(target=deleteFile, args=(filePath, True))
        deletionThread.start()
        return await send_file(filePath, as_attachment=True, attachment_filename='totally_normal_file.png')
    except Exception as e:
        print('couldnt save file')
        print(e)
        return 'Server encountered an error, try again later...', 502

def deleteFile(filePath, delay):
    """
    Delete a file.

    :param filePath: path of the file to be deleted.
    :param delay: Flag to specify if there should be a delay before deletion.
    :return: None
    """
    if delay:
        time.sleep(0.5)
    try:
        os.remove(filePath)
    except Exception as e:
        print('failed to delete file at ' + filePath)
        print(e)




async def handleGetInsertPlanInfo(request):
    """
    Async method to handle the GET request for retrieving information for inserting a plan.

    :param request: The request object.
    :return: A JSON response containing the action form ID addon and the plan information block content.
    """
    result = await getPlanInfoForInsertPage()
    if not result:
        return 'Server encountered an error, try again later...', 502
    actionFormIdAddon, planInfoBlockContent = result
    answer = {
        'actionFormIdAddon' : actionFormIdAddon,
        'planInfoBlockContent' : planInfoBlockContent
    }
    return jsonify(answer)
    



async def generateReadPage(request):
    """
    Generate and return the read page.

    :param request: The request object.
    :return: The rendered read page.
    """
    cache_buster = str(time.time())
    return await render_template('read.html', cache_buster=cache_buster)


async def handleRead(request):
    """
    Handle read request.

    :param request: The request object.
    :return: The response string and status code.
    """
    requestData = await getReadRequestData(request)
    if not requestData:
        return '', 400
    result = await WAITER.runTask('read', requestData)
    #result = ''
    if result == None:
        return 'Server encountered an error, try again later...', 502
    elif result == False:
        return 'You shall never know, for the knoledge only reveals itself to the ones worthy.', 403
    # elif the file is not right - was too corrupted or wasnt modified in stega
    return await handleReadResult(result)


async def getReadRequestData(request):
    """
    :param request: The HTTP request object.
    :return: The read request data as a dictionary, or None if an error occurs.
    """

    try:

        form = await request.form
        files = await request.files
        data = {}
        formType = form.get('form-type')
        if formType != 'read':
            return None
        gotModFile = await appendReceivedModFileToRequestData(files, data)
        if not gotModFile:
            return None
        gotMetadata = await appendMetadataToRequestData(form, data)
        if not gotMetadata:
            return None
        try:
            data['userHash'] = session['username']
        except:
            print('failed to get user hash')
            return None
        return data
    except Exception as e:
        print('returning 400')
        print(e)
        return None


async def appendReceivedModFileToRequestData(files, data):
    """
    :param files: dictionary containing the files received
    :param data: dictionary to store the modified file and its type
    :return: success (bool) indicating if the file was successfully appended to data

    This method attempts to append the received modified file to the request data.
    It saves the file to disk, reads it as bytes, adds it to the data dictionary,
    and sets the modified file type based on its file extension.

    Returns True if the file was successfully appended to data, False otherwise.
    """
    success = False
    for _ in range(2):
        if not success:
            try:
                modFile = files.get('modified-file')
                filePath = getFilePathToSave(modFile.filename)
                await modFile.save(filePath)
                async with aiofiles.open(filePath, 'rb') as f:
                    byteFile = await f.read()
                deleteFile(filePath, False)
                data['modifiedFile'] = byteFile
                data['modifiedFileType'] = filePath.split('.')[-1]
                success = True
            except Exception as e:
                print('failed to get modified file')
                print(e)
    return success
    

async def appendMetadataToRequestData(form, data):
    """
    :param form: A dictionary containing form data.
    :param data: A dictionary containing request data.

    :return: A boolean value indicating whether the metadata was successfully appended to the request data.

    This method appends the metadata from the 'form' dictionary to the 'data' dictionary. It retrieves the metadata using the key 'metadata' from the 'form' dictionary, and adds it with the same key to the 'data' dictionary.

    If the metadata is successfully appended, the method returns True. If an exception occurs during the process, such as failing to get the metadata, the method prints an error message along with the exception and returns False.
    """
    try:
        metadata = form.get('metadata')
        data['metadata'] = metadata
        return True
    except Exception as e:
        print('failed to get metadata')
        print(e)
        return False


async def handleReadResult(result):
    """
    Saves the file bytes to disk, starts a deletion thread, and returns the file for downloading.

    :param result: The file bytes to handle.
    :return: The downloaded file as an attachment.
    """
    fileBytes = result
    filePath = getFilePathToSave( '.zip')
    try:
        async with aiofiles.open(filePath, 'wb') as f:
            await f.write(fileBytes)
        
        deletionThread = threading.Thread(target=deleteFile, args=(filePath, True))
        deletionThread.start()
        return await send_file(filePath, as_attachment=True, attachment_filename='very_much_not_secret_file.zip')
    except Exception as e:
        print('couldnt save file')
        print(e)
        return 'Server encountered an error, try again later...', 502



async def generatePlansPage(request):
    """
    Generates the plans page.

    :param request: The request object.
    :return: The rendered template containing the plans page.
    :rtype: str
    """

    result = await WAITER.runTask('loadPlans', {'userHash' : session['username'] if 'username' in session else None})

    if not result:
        return 'Server encountered an error, try again later...', 502
    plans, currentPlanId = result
    cache_buster = str(time.time())
    return await render_template('plans.html', plans=plans, currentPlanId=currentPlanId if currentPlanId else -1, cache_buster=cache_buster)



async def handlePlanFormSubmit(request):
    """
    :param request: the request object passed from the client
    :return: if successful, it redirects to /home; if there's an error, it returns an error message along with error code 502
    """

    form = await request.form
    planId = form.get('plan-id')
    result = await WAITER.runTask('updatePlan', {'userHash' : session['username'], 'planId' : planId})
    if result:
        session['plan'] = planId
        return redirect('/home')
    return 'Server encountered an error, try again later...', 502



async def logout(request):
    """
    :param request: The HTTP request object.
    :return: None.

    This method logs out the user by clearing the session data. It then prints a message indicating that the session has ended and redirects the user to the login page.
    """
    session.clear()  # Clear the session data
    return redirect('/login')



async def getTest(request):
    """
        :param request: the HTTP request object
        :return: the rendered template 'test.html' with a cache buster as a keyword argument
    """
    #return abort(404)
    cache_buster = str(time.time())
    return await render_template('test.html', cache_buster=cache_buster)



async def handleGenerateImage(request):
    """
    :param request: The request object received from the client.
    :return: If successful, returns the generated image as a JSON response. If an error occurs, returns an error message and status code.

    This method handles the generation of an image based on the provided prompt, style, and size. It makes a call to the OpenAI API to generate the image and then downloads and saves it locally. The saved image is then returned to the client.

    If any exceptions occur during the process, an error message is printed and an error response is returned.

    Example usage:
        response = await handleGenerateImage(request)
    """
    timeout = 10
    form = await request.form
    prompt = form.get('prompt')
    style = form.get('style')
    size = form.get('size')

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.openai.com/v1/images/generations',
                headers={
                    'Authorization': f'Bearer {OPENAI_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'prompt': prompt,
                    'size': size,
                    'style': style,
                    'response_format': 'b64_json',
                    #'model': 'dall-e-3'
                },
                timeout=timeout
            )
        
            response.raise_for_status()  # Raise an exception for HTTP error responses
            return jsonify(response.json())

            # Assuming the API returns a URL to the generated image
            imageUrl = data['data'][0]['url']

            # Download the image and save it locally
            imageResponse = await client.get(imageUrl)
        imageData = imageResponse.content

        # Save the image to a file
        imagePath = getFilePathToSave(f'{prompt[:10]}_{size}_{style}.png')
        with open(imagePath, 'wb') as imageFile:
            imageFile.write(imageData)

        return await send_file(imagePath, mimetype='image/png')

    except Exception as e:
        print('An error occurred while trying to generate image')
        print(e)
        return 'An error occured while trying to generate the image.', 500





# session updating

async def updateSessionTimeoutOnActivity(request):
    """
    :param request: The request object represents the HTTP request made by the client.
    :return: Returns a tuple containing a response and HTTP status code. In the case where the 'updateSessionTimeout' method returns False, an empty string and HTTP status code 200 is returned.
    """
    ans = await updateSessionTimeout()
    if not ans:
        ans = '', 200
    return ans

async def updateSessionTimeout():
    """
    Updates the session timeout by checking the last activity time.

    :return: None
    """
    if 'username' in session:
        lastActivity = session.get('last_activity')
        if lastActivity is not None and time.time() - lastActivity > 15*60:
            # Session expired, redirect to login page
            return await logout()

        session['last_activity'] = time.time()  # Update last activity time
    else:
        return redirect('/login')













if __name__ == '__main__':
    app.run(host='0.0.0.0')
