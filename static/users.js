let $signupPassword = $('#signup_password');
let $signupPassword2 = $('#password2');
let $signupUsername = $('#signup_username');
let $email = $('#email');
let $userImage = $('#user_image');
let $signupButton = $('#signup_button');
let $loginButton = $
let $modalBody = $('.modal-body')

// validation of signup form
$signupButton.on('click', async function(event){
    event.preventDefault();
    if ($('.error-div').length > 0){
        $('.error-div').remove()
    }
    const passwordRegex = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$/;
    //validate matching passwords
    if ($signupPassword.val() !== $signupPassword2.val()){
        $errorDiv = $('<div class="alert alert-danger" id="error-div">Passwords do not match. Please try again</div>');
        $modalBody.append($errorDiv);
    }
    //validate secure password
    else if (!passwordRegex.test($signupPassword.val())){
        $errorDiv = $('<div class="alert alert-danger" id="error-div">Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, and one number</div>');
        $modalBody.append($errorDiv);
    }
    else {
        response = await signupViaAxios();
        if (response['error']){
            returnedErrorHandler(response);
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

//deal with returned error
function returnedErrorHandler(response){
    if (response['error'] === 'Email already taken'){
        $errorDiv = $('<div class="alert alert-danger" id="error-div">Email already registered. Please try logging in.</div>')
        $modalBody.append($errorDiv)
    }
    else if (response['error'] === 'Username already taken'){
        $errorDiv = $('<div class="alert alert-danger" id="error-div">Username already registered. Please try logging in.</div>')
        $modalBody.append($errorDiv)
    }
}