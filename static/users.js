let $signupPassword = $('#signup_password');
let $signupPassword2 = $('#password2');
let $signupUsername = $('#signup_username');
let $loginUsername = $('#login_username');
let $loginPassword = $('#login_password');
let $email = $('#email');
let $userImage = $('#user_image');
let $signupButton = $('#signup_button');
let $loginButton = $('#login_button')
let $modalBody = $('.modal-body')
let $cancelButton = $('.cancel-button');
let $closeButton = $('.close-button');

// validation of signup form
$signupButton.on('click', async function(event){
    event.preventDefault();
    $modalBody.find('.error-div').remove();
    const passwordRegex = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$/;
    //validate matching passwords
    if ($signupPassword.val() !== $signupPassword2.val()){
        $errorDiv = $('<div class="alert alert-danger error-div">Passwords do not match. Please try again</div>');
        $modalBody.append($errorDiv);
    }
    //validate secure password
    else if (!passwordRegex.test($signupPassword.val())){
        $errorDiv = $('<div class="alert alert-danger error-div">Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, and one number</div>');
        $modalBody.append($errorDiv);
    }
    else {
        response = await signupViaAxios();
        if (response['error']){
            signupReturnedErrorHandler(response);
        }
        else {
            location.reload();
        }
    }
});

//send data via axios
async function signupViaAxios(){
    const username = $signupUsername.val();
    const password = $signupPassword.val();
    const email = $email.val();
    const userImage = $userImage.val();
    const userData = {username: username, password: password, email: email, userImage: userImage};
    const response = await axios.post('/signup', userData)
    return response.data
}

function signupReturnedErrorHandler(response){
    if (response['error'] === 'Email already taken'){
        $errorDiv = $('<div class="alert alert-danger error-div">Email already registered. Please try logging in.</div>');
        $modalBody.append($errorDiv);
    }
    else if (response['error'] === 'Username already taken'){
        $errorDiv = $('<div class="alert alert-danger error-div">Username already registered. Please try logging in.</div>');
        $modalBody.append($errorDiv);
    }
}

//validation of login form
$loginButton.on('click', async function(event){
    event.preventDefault();
    $modalBody.find('.error-div').remove();
    response = await loginViaAxios();
    if (response['error']){
        loginReturnedErrorHandler(response);
    }
    else {
        location.reload();
    }
});

//send data via axios
async function loginViaAxios(){
    const username = $loginUsername.val();
    const password = $loginPassword.val();
    const userData = {username: username, password: password};
    const response = await axios.post('/login', userData);
    return response.data;
}

//deal with returned error
function loginReturnedErrorHandler(response){
    if (response['error'] === 'Invalid username'){
        $errorDiv = $('<div class="alert alert-danger error-div">Invalid username</div>');
        $modalBody.append($errorDiv);
    }
    else if (response['error'] === 'Invalid password'){
        $errorDiv = $('<div class="alert alert-danger error-div">Invalid password</div>');
        $modalBody.append($errorDiv);
    }
}

//clear forms and errors when cancel button is pressed
$cancelButton.on('click', function(event){
    event.preventDefault();
    $modalBody.find('.error-div').remove();
    $signupPassword.val('');
    $signupPassword2.val('');
    $signupUsername.val('');
    $loginUsername.val('');
    $loginPassword.val('');
    $email.val('');
    $userImage.val('');
})

//clear forms and errors when close button is pressed
$closeButton.on('click', function(event){
    event.preventDefault();
    $modalBody.find('.error-div').remove();
    $signupPassword.val('');
    $signupPassword2.val('');
    $signupUsername.val('');
    $loginUsername.val('');
    $loginPassword.val('');
    $email.val('');
    $userImage.val('');
})