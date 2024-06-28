let $signupPassword = $('#signup_password');
let $signupPassword2 = $('#password2');
let $signupUsername = $('#signup_username');
let $loginUsername = $('#login_username');
let $loginPassword = $('#login_password');
let $signupEmail = $('#signup_email');
let $email = $('#email');
let $updatePassword = $('#update_password');
let $updatePassword2 = $('#update_password2');
let $userImage = $('#user_image');
let $signupButton = $('#signup_button');
let $loginButton = $('#login_button');
let $updatePasswordButton = $('.update-password');
let $forgotLink = $('.forgot-link')
let $sendreminderButton = $('#send_reminder_button');
let $sendResetButton = $('#send_reset_button');
let $modalBody = $('.modal-body')
let $cancelButton = $('.cancel-button');
let $closeButton = $('.close-button');
let $mainContent = $('.main-content');

// validation of signup form
$signupButton.on('click', async function(event){
    console.log('signup button clicked');
    event.preventDefault();
    $modalBody.find('.error-div').remove();
    const passwordRegex = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$/;
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
    //validate all data is present
    if ($signupUsername.val() === '' || $signupPassword.val()=== '' || $signupPassword2.val() === '' || $signupEmail.val() === ''){
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">All fields are required.</div>');
        $modalBody.append($errorDiv);
    }
    //validate matching passwords
    else if ($signupPassword.val() !== $signupPassword2.val()){
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Passwords do not match.</div>');
        $modalBody.append($errorDiv);
    }
    //validate secure password
    else if (!passwordRegex.test($signupPassword.val())){
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, one number, and one special character</div>');
        $modalBody.append($errorDiv);
    }
    //validate valid email
    else if (!emailRegex.test($signupEmail.val())){
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Email does not appear valid</div>');
        $modalBody.append($errorDiv);
    }
    //validate username & email are unique
    else {
        let response = await signupViaAxios();
        if (response['error']){
            signupReturnedErrorHandler(response);
        }
        else {
            pageReload();
            let $welcomeDiv = $(`<div class="alert alert-success welcome-div">Welcome ${$loginUsername.val()}</div>`);
            $mainContent.prepend($welcomeDiv);
        }
    }
});

//pageReload function for testing purposes
function pageReload(){
    window.location.reload();
}

//send signup data via axios
async function signupViaAxios(){
    const username = $signupUsername.val();
    const password = $signupPassword.val();
    const email = $signupEmail.val();
    const userImage = $userImage.val();
    const userData = {username: username, password: password, email: email, userImage: userImage};
    const response = await axios.post('/signup', userData)
    return response.data
}

//deal with signup returned error
function signupReturnedErrorHandler(response){
    if (response['error'] === 'Email already taken'){
        console.log('email already taken if');
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Email already registered. Please try logging in.</div>');
        $modalBody.append($errorDiv);
    }
    else if (response['error'] === 'Username already taken'){
        console.log('username already taken if');
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Username already registered. Please try logging in.</div>');
        $modalBody.append($errorDiv);
    }
}

//validation of login form
$loginButton.on('click', async function(event){
    event.preventDefault();
    $modalBody.find('.error-div').remove();
    //validate all data is present
    if ($loginUsername.val() === '' || $loginPassword.val()=== ''){
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">All fields are required.</div>');
        $modalBody.append($errorDiv);
    }
    else {
        let response = await loginViaAxios();
        if(response['error']){
            loginReturnedErrorHandler(response);
        }
        else {
            pageReload();
            let $welcomeDiv = $(`<div class="alert alert-success welcome-div">Welcome ${$loginUsername.val()}</div>`);
            $mainContent.prepend($welcomeDiv);
        }
    }
});

//send login data via axios
async function loginViaAxios(){
    console.log('running loginViaAxios');
    const username = $loginUsername.val();
    const password = $loginPassword.val();
    const userData = {username: username, password: password};
    const response = await axios.post('/login', userData);
    console.log(response);
    return response.data;
}

//deal with login returned error
function loginReturnedErrorHandler(response){
    console.log('running loginReturnedErrorHandler function');
    if (response['error'] === 'Invalid username'){
        console.log('invalid username if');
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Invalid username</div>');
        $modalBody.append($errorDiv);
    }
    else if (response['error'] === 'Invalid password'){
        console.log('invalid password if');
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Invalid password</div>');
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
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Email not in database. Please signup.</div>');
        $modalBody.append($errorDiv);
    }
    if (response['success']){
        let $errorDiv = $('<div id="edit-css" class="alert alert-success error-div">Email sent</div>');
        $modalBody.append($errorDiv)
    }
});

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
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Email not in database. Please signup.</div>');
        $modalBody.append($errorDiv);
    }
    if (response['success']){
        let $errorDiv = $('<div id="edit-css" class="alert alert-success error-div">Email sent</div>');
        $modalBody.append($errorDiv);
    }
});

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
$updatePasswordButton.on('click', async function(event){
    console.log('update password button clicked')
    event.preventDefault();
    $modalBody.find('.error-div').remove();
    const passwordRegex = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$/;
    if ($updatePassword.val() !== $updatePassword2.val()){
        console.log('passwords not matching if');
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Passwords do not match.</div>');
        $modalBody.append($errorDiv);
    }
    else if  (!passwordRegex.test($updatePassword.val())){
        console.log('passwords not secure if')
        let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, one number, and one special character</div>');
        $modalBody.append($errorDiv);
    }
    else {
        let response = await updatePasswordViaAxios();
        if (response['error']){
            console.log('entering error if')
            let $errorDiv = $('<div id="edit-css" class="alert alert-danger error-div">Something went wrong. Please try again</div>')
            $modalBody.append($errorDiv);
        }
        if (response['success']){
            console.log('entering success if')
            let $errorDiv = $('<div id="edit-css" class="alert alert-success error-div">Password updated</div>');
            $modalBody.append($errorDiv);
        }
    }
});

//send updated password via axios
async function updatePasswordViaAxios(){
    const password = $updatePassword.val()
    const data = {password: password};
    const response = await axios.post('/updatepassword', data);
    return response.data;
};

//clear forms and errors when cancel button is pressed
$cancelButton.on('click', function(event){
    $modalBody.find('.error-div').remove();
    $signupPassword.val('');
    $signupPassword2.val('');
    $signupUsername.val('');
    $loginUsername.val('');
    $loginPassword.val('');
    $updatePassword.val('');
    $updatePassword2.val('');
    $signupEmail.val('');
    $email.val('');
    $userImage.val('');
});

//clear forms and errors when close button is pressed
$closeButton.on('click', function(event){
    $modalBody.find('.error-div').remove();
    $signupPassword.val('');
    $signupPassword2.val('');
    $signupUsername.val('');
    $loginUsername.val('');
    $loginPassword.val('');
    $updatePassword.val('');
    $updatePassword2.val('');
    $signupEmail.val('');
    $email.val('');
    $userImage.val('');
});


$forgotLink.on('click', function(event){
    $modalBody.find('.error-div').remove();
});