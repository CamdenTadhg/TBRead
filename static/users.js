let $signupPassword = $('#signup_password');
let $signupPassword2 = $('#password2');
let $signupUsername = $('#signup_username');
let $loginUsername = $('#login_username');
let $loginPassword = $('#login_password');
let $signup_email = $('#signup_email');
let $email = $('#email');
let $password = $('#password');
let $userImage = $('#user_image');
let $signupButton = $('#signup_button');
let $loginButton = $('#login_button');
let $updatePassword = $('.update-password');
let $forgotLink = $('.forgot-link')
let $sendreminderButton = $('#send_reminder_button');
let $sendResetButton = $('#send_reset_button');
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
        let $errorDiv = $('<div class="alert alert-danger error-div">Passwords do not match. Please try again</div>');
        $modalBody.append($errorDiv);
    }
    //validate secure password
    else if (!passwordRegex.test($signupPassword.val())){
        let $errorDiv = $('<div class="alert alert-danger error-div">Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, and one number</div>');
        $modalBody.append($errorDiv);
    }
    else {
        let response = await signupViaAxios();
        if (response['error']){
            signupReturnedErrorHandler(response);
        }
        else {
            location.reload();
        }
    }
});

//send signup data via axios
async function signupViaAxios(){
    const username = $signupUsername.val();
    const password = $signupPassword.val();
    const email = $signup_email.val();
    const userImage = $userImage.val();
    const userData = {username: username, password: password, email: email, userImage: userImage};
    const response = await axios.post('/signup', userData)
    return response.data
}

//deal with signup returned error
function signupReturnedErrorHandler(response){
    if (response['error'] === 'Email already taken'){
        let $errorDiv = $('<div class="alert alert-danger error-div">Email already registered. Please try logging in.</div>');
        $modalBody.append($errorDiv);
    }
    else if (response['error'] === 'Username already taken'){
        let $errorDiv = $('<div class="alert alert-danger error-div">Username already registered. Please try logging in.</div>');
        $modalBody.append($errorDiv);
    }
}

//validation of login form
$loginButton.on('click', async function(event){
    event.preventDefault();
    $modalBody.find('.error-div').remove();
    let response = await loginViaAxios();
    if (response['error']){
        loginReturnedErrorHandler(response);
    }
    else {
        location.reload();
    }
});

//send login data via axios
async function loginViaAxios(){
    const username = $loginUsername.val();
    const password = $loginPassword.val();
    const userData = {username: username, password: password};
    const response = await axios.post('/login', userData);
    return response.data;
}

//deal with login returned error
function loginReturnedErrorHandler(response){
    if (response['error'] === 'Invalid username'){
        let $errorDiv = $('<div class="alert alert-danger error-div">Invalid username</div>');
        $modalBody.append($errorDiv);
    }
    else if (response['error'] === 'Invalid password'){
        let $errorDiv = $('<div class="alert alert-danger error-div">Invalid password</div>');
        $modalBody.append($errorDiv);
    }
}

//send username reminder event handler
$sendreminderButton.on('click', async function(event){
    console.log('send reminder button clicked')
    event.preventDefault();
    $modalBody.find('.error-div').remove();
    let response = await usernameReminderViaAxios();
    if (response['error']) {
        let $errorDiv = $('<div class="alert alert-danger error-div">Email not in database. Please signup.</div>');
        $modalBody.append($errorDiv);
    }
    if (response['success']){
        let $errorDiv = $('<div class="alert alert-success error-div">Email sent</div>');
        $modalBody.append($errorDiv)
    }
})

//send email via axios to send username reminder
async function usernameReminderViaAxios(){
    console.log('entering usernameReminderViaAxios');
    const email = $email.val();
    const data = {email: email};
    const response = await axios.post('/forgotusername', data);
    console.log(response);
    return response.data;
}

//send password reset email event handler
$sendResetButton.on('click', async function(event){
    event.preventDefault();
    $modalBody.find('.error-div').remove();
    let response = await passwordResetViaAxios();
    if (response['error']){
        let $errorDiv = $('<div class="alert alert-danger error-div">Email not in database. Please signup.</div>');
        $modalBody.append($errorDiv);
    }
    if (response['success']){
        let $errorDiv = $('<div class="alert alert-success error-div">Email sent</div>');
        $modalBody.append($errorDiv);
    }
})

//send email via axios to send password reset
async function passwordResetViaAxios(){
    const email = $email.val()
    console.log(email);
    const data = {email: email};
    const response = await axios.post('/forgotpassword', data);
    console.log(response);
    return response.data;
}

//update password event handler
$updatePassword.on('click', async function(event){
    event.preventDefault();
    $modalBody.find('.error-div').remove();
    let response = await updatePasswordViaAxios();
    console.log(response);
    if (response['error']){
        console.log('entering error if')
        let $errorDiv = $('<div class="alert alert-danger error-div">Something went wrong. Please try again</div>')
        $modalBody.append($errorDiv);
    }
    if (response['success']){
        console.log('entering success if')
        let $errorDiv = $('<div class="alert alert-success error-div">Password updated</div>');
        $modalBody.append($errorDiv);
    }
})

//send updated password via axios
async function updatePasswordViaAxios(){
    const password = $password.val()
    const data = {password: password};
    const response = await axios.post('/updatepassword', data);
    return response.data;
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

$forgotLink.on('click', function(event){
    event.preventDefault();
    $modalBody.find('.error-div').remove();
})