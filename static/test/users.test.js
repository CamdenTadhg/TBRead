//FAILING. The setting of signupViaAxiosSpy to return value of error:"yes" in the previous test is carrying over into this test, but the spy should have been unassigned in the afterEach function so I don't understand why this is happening. 
describe('signupViaAxios function', () => {
    let axiosPostSpy;

    beforeEach(() => {
        // Set up spies and DOM elements
        axiosPostSpy = spyOn(axios, 'post').and.returnValue(Promise.resolve({ data: { success: true } }));

        // Set up DOM elements
        $signupUsername = $('<input id="signupUsername" type="text">').appendTo('body');
        $signupEmail = $('<input id="signupEmail" type="email">').appendTo('body');
        $signupPassword = $('<input id="signupPassword" type="password">').appendTo('body');
        $userImage = $('<input id="userImage" type="text">').appendTo('body');
    });

    afterEach(() => {
        // Clean up DOM elements
        $signupUsername.remove();
        $signupEmail.remove();
        $signupPassword.remove();
        $userImage.remove();
    });

    it('sends signup data via axios and returns response data', async () => {
        // Set values to DOM elements
        $signupUsername.val('testuser15');
        $signupEmail.val('testuser@test.com');
        $signupPassword.val('Password1!');
        $userImage.val('imagePath');

        const response = await signupViaAxios();

        expect(axiosPostSpy).toHaveBeenCalledWith('/signup', {
            username: 'testuser15',
            password: 'Password1!',
            email: 'testuser@test.com',
            userImage: 'imagePath'
        });
        expect(response).toEqual({ success: true });
    });
});

//FAILING. Actual code works fine on the front end. Test is not entering corresponding if statements, despite statement condition registering as true. 
describe('signupReturnedErrorHandler', () => {
    beforeEach(() => {
        //set up DOM elements
        $modalBody = $('<div class="modal-body"></div>').appendTo('body');
    });

    afterEach(() => {
        //clean up DOM elements
        $modalBody.remove();
    })

    it('returns correct error message for duplicate email error', () => {
        const response = {error: 'Email already taken'};
        signupReturnedErrorHandler(response);
        expect($modalBody.find('.error-div').text()).toBe('Email already registered. Please try logging in.');
    });

    it('returns correct error message for duplicate username error', () => {
        const response = {error: 'Username already taken'};
        signupReturnedErrorHandler(response);
        expect($modalBody.find('.error-div').text()).toBe('Username already registered. Please try logging in.');
    });
});



//FAILING. The setting of loginViaAxiosSpy to return value of error:"yes" in the previous test is carrying over into this test, but the spy should have been unassigned in the afterEach function so I don't understand why this is happening. 
describe('loginViaAxios', () => {
    let axiosPostSpy;

    beforeEach(() => {
    //create spies
    axiosPostSpy = spyOn(axios, 'post').and.returnValue(Promise.resolve({data: {success: true}}));

    //set up DOM
    $loginUsername = $('<input type="text" id="loginUsername">');
    $loginPassword = $('<input type="text" id="loginPassword">');
    });

    afterEach(() => {
        //clean up DOM
        $loginUsername.remove();
        $loginPassword.remove();
    });

    it('sends login data via axios and returns response data', async () => {
        $loginUsername.val('camdentadhg');
        $loginPassword.val('lkajslkjas');
        const response = await loginViaAxios();

        expect(axiosPostSpy).toHaveBeenCalledWith('/login', {username: 'camdentadhg', password: 'lkajslkjas'});
        expect(response).toEqual({success: true});
    });
});

//FAILING. I think this is also an issue with the spy not being undone because it runs fine on its own. It's not running the actual function. 
describe('loginReturnedErrorHandler', () => {
    beforeEach(() => {
        //set up DOM
        $modalBody = $('<div class="modalBody"></div>').appendTo('body');
    });

    afterEach(() => {
        //clean up DOM
        $modalBody.remove();
    });

    it('returns correct error message for invalid username', () => {
        const response = {error: 'Invalid username'};
        loginReturnedErrorHandler(response);

        expect($modalBody.find('.error-div')[0].innerText).toEqual('Invalid username');
    });

    it('returns correct error message for invalid password', () => {
        const response = {error: 'Invalid password'};
        loginReturnedErrorHandler(response);

        expect($modalBody.find('.error-div')[0].innerText).toEqual('Invalid password');
    });
});



describe('usernameReminderViaAxios', () => {
    let axiosPostSpy;

    beforeEach(() => {
        //create spy
        axiosPostSpy = spyOn(axios, 'post').and.returnValue(Promise.resolve({data: {success: true}}));
        //set up the DOM
        $email = $('<input type="text" id="email">');
    });

    afterEach(() => {
        //clean up the DOM
        $email.remove();
    });

    it('sends the appropriate data via axios and returns the response', async () => {
        $email.val('camden@test.com');
        let response = await usernameReminderViaAxios();

        expect(axiosPostSpy).toHaveBeenCalledWith('/forgotusername', {email: 'camden@test.com'});
        expect(response).toEqual({success: true});
    });
});



describe('passwordResetViaAxios', () => {
    let axiosPostSpy;
    beforeEach(() => {
        //create spy
        axiosPostSpy = spyOn(axios, 'post').and.returnValue(Promise.resolve({data: {success: true}}));

        //set up DOM
        $email = $('<input type="text" id="email">');
    });

    afterEach(() => {
        //clean up DOM
        $email.remove();
    });

    it('sends email via axios and returns response', async () => {
        $email.val('camden@test.com');
        const response = await passwordResetViaAxios();

        expect(axiosPostSpy).toHaveBeenCalledWith('/forgotpassword', {email: 'camden@test.com'});
        expect(response).toEqual({success: true});
    });
});



describe('updatePasswordViaAxios', () => {
    let axiosPostSpy;
    beforeEach(() => {
        //create spy
        axiosPostSpy = spyOn(axios, 'post').and.returnValue(Promise.resolve({data: {success: true}}));
        //set up DOM
        $updatePassword = $('<input type="text" id="update_password">').appendTo('body');
    });

    afterEach(() => {
        //clean up DOM
        $updatePassword.remove();
    })

    it('sends data via axios and returns correct result', async () => {
        $updatePassword.val('Password1!');
        const response = await updatePasswordViaAxios();

        expect(axiosPostSpy).toHaveBeenCalledWith('/updatepassword', {password: 'Password1!'});
        expect(response).toEqual({success: true});
    })
});

describe('cancel button event handler', () => {
    beforeEach(() => {
        //set up DOM
        $cancelButton = $('<button class="cancel-button">Cancel</button>').appendTo('body');
        $modalBody = $('<div class="modal-body><div class="alert alert-danger error-div">Something went wrong. Please try again</div></div>').appendTo('body');
        $signupPassword = $('<input type="text" id="signup_password">').appendTo('body');
        $signupPassword2 = $('<input type="text" id="password2">').appendTo('body');
        $signupUsername = $('<input type="text" id="signup_username">').appendTo('body');
        $loginUsername = $('<input type="text" id="login_username">').appendTo('body');
        $loginPassword = $('<input type="text" id="login_password">').appendTo('body');
        $email = $('<input type="email" id="email">').appendTo('body');
        $userImage = $('<input type="text" id="user_image">').appendTo('body');
        $updatePassword = $('<input type="text" id="update_password">').appendTo('body');
        $updatePassword2 = $('<input type="text" id="update_password2">').appendTo('body');
        $signupEmail = $('<input type="text" id="signup_email">').appendTo('body');

        //attach the event handler
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
    });

    afterEach(() => {
        //Clean up DOM
        $cancelButton.remove();
        $modalBody.remove();
        $signupPassword.remove();
        $signupPassword2.remove();
        $signupUsername.remove();
        $loginUsername.remove();
        $loginPassword.remove();
        $email.remove();
        $userImage.remove();
        $updatePassword.remove();
        $updatePassword2.remove();
        $signupEmail.remove();
    });

    it('clears all fields and errors when cancel button is pressed', () => {  
        $signupPassword.val('Password1!');
        $signupPassword2.val('Password1!');
        $signupUsername.val('testuser');
        $loginUsername.val('testuser');
        $loginPassword.val('Password1!');
        $updatePassword.val('Password1!');
        $updatePassword2.val('Password1!');
        $signupEmail.val('test@test.com');
        $email.val('test@test.com');
        $userImage.val('image url');

        const event = $.Event('click');
        $cancelButton.trigger(event);

        expect($modalBody.find('.error-div').length).toBe(0);
        expect($signupPassword.val()).toEqual('');
        expect($signupPassword2.val()).toEqual('');
        expect($signupUsername.val()).toEqual('');
        expect($loginUsername.val()).toEqual('');
        expect($loginPassword.val()).toEqual('');
        expect($updatePassword.val()).toEqual('');
        expect($updatePassword2.val()).toEqual('');
        expect($signupEmail.val()).toEqual('');
        expect($email.val()).toEqual('');
        expect($userImage.val()).toEqual('');
    });
});

describe('close button event handler', () => {
    beforeEach(() => {
        //set up DOM
        $closeButton = $('<button class="close-button">X</button>').appendTo('body');
        $modalBody = $('<div class="modal-body><div class="alert alert-danger error-div">Something went wrong. Please try again</div></div>').appendTo('body');
        $signupPassword = $('<input type="text" id="signup_password">').appendTo('body');
        $signupPassword2 = $('<input type="text" id="password2">').appendTo('body');
        $signupUsername = $('<input type="text" id="signup_username">').appendTo('body');
        $loginUsername = $('<input type="text" id="login_username">').appendTo('body');
        $loginPassword = $('<input type="text" id="login_password">').appendTo('body');
        $email = $('<input type="email" id="email">').appendTo('body');
        $userImage = $('<input type="text" id="user_image">').appendTo('body');
        $updatePassword = $('<input type="text" id="update_password">').appendTo('body');
        $updatePassword2 = $('<input type="text" id="update_password2">').appendTo('body');
        $signupEmail = $('<input type="text" id="signup_email">').appendTo('body');

        //attach the event handler
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
    });

    afterEach(() => {
        //Clean up DOM
        $closeButton.remove();
        $modalBody.remove();
        $signupPassword.remove();
        $signupPassword2.remove();
        $signupUsername.remove();
        $loginUsername.remove();
        $loginPassword.remove();
        $email.remove();
        $userImage.remove();
        $updatePassword.remove();
        $updatePassword2.remove();
        $signupEmail.remove();
    });

    it('clears all fields and errors when cancel button is pressed', () => {  
        $signupPassword.val('Password1!');
        $signupPassword2.val('Password1!');
        $signupUsername.val('testuser');
        $loginUsername.val('testuser');
        $loginPassword.val('Password1!');
        $updatePassword.val('Password1!');
        $updatePassword2.val('Password1!');
        $signupEmail.val('test@test.com');
        $email.val('test@test.com');
        $userImage.val('image url');

        const event = $.Event('click');
        $closeButton.trigger(event);

        expect($modalBody.find('.error-div').length).toBe(0);
        expect($signupPassword.val()).toEqual('');
        expect($signupPassword2.val()).toEqual('');
        expect($signupUsername.val()).toEqual('');
        expect($loginUsername.val()).toEqual('');
        expect($loginPassword.val()).toEqual('');
        expect($updatePassword.val()).toEqual('');
        expect($updatePassword2.val()).toEqual('');
        expect($signupEmail.val()).toEqual('');
        expect($email.val()).toEqual('');
        expect($userImage.val()).toEqual('');
    });
});

describe('forgot link event handler', () => {
    beforeEach(() => {
        //set up DOM
        $modalBody = $('<div class="modal-body><div class="alert alert-danger error-div">Something went wrong. Please try again</div></div>').appendTo('body');
        $forgotLink = $('<button class="forgot-link">Forgot Username/Password?</button>')
    });

    afterEach(() => {
        //clean up DOM
        $modalBody.remove();
        $forgotLink.remove();
    });

    it('should remove all error messages when forgot link is clicked', () => {
        const event = $.Event('click');
        $forgotLink.trigger(event);

        expect($modalBody.find('.error-div').length).toBe(0);
    });
});

describe('validation of signup form', () => {
    let signupViaAxiosSpy, signupReturnedErrorHandlerSpy, preventDefaultSpy, pageReloadSpy;
    let $signupUsername, $signupEmail, $signupPassword, $signupPassword2, $signupButton, $modalBody;

    beforeEach(() => {
        // Set up spies
        signupViaAxiosSpy = jasmine.createSpy('signupViaAxios').and.returnValue(Promise.resolve({}));
        signupReturnedErrorHandlerSpy = jasmine.createSpy('signupReturnedErrorHandler');
        pageReloadSpy = jasmine.createSpy('pageReload');

        // Assign spies to global scope
        window.signupViaAxios = signupViaAxiosSpy;
        window.signupReturnedErrorHandler = signupReturnedErrorHandlerSpy;
        window.pageReload = pageReloadSpy;

        // Set up DOM elements
        $signupUsername = $('<input id="signupUsername" type="text">').appendTo('body');
        $signupEmail = $('<input id="signupEmail" type="email">').appendTo('body');
        $signupPassword = $('<input id="signupPassword" type="password">').appendTo('body');
        $signupPassword2 = $('<input id="signupPassword2" type="password">').appendTo('body');
        $signupButton = $('<button id="signupButton">Sign Up</button>').appendTo('body');
        $modalBody = $('<div class="modal-body"></div>').appendTo('body');

        // Attach event handler to signup button
        $signupButton.on('click', async function(event) {
            event.preventDefault();
            $modalBody.find('.error-div').remove();
            const passwordRegex = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$/;
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            // Validate all data is present
            if ($signupUsername.val() === '' || $signupPassword.val() === '' || $signupPassword2.val() === '' || $signupEmail.val() === '') {
                let $errorDiv = $('<div class="alert alert-danger error-div">Username, email, and password are required.</div>');
                $modalBody.append($errorDiv);
            }
            // Validate matching passwords
            else if ($signupPassword.val() !== $signupPassword2.val()) {
                let $errorDiv = $('<div class="alert alert-danger error-div">Passwords do not match.</div>');
                $modalBody.append($errorDiv);
            }
            // Validate secure password
            else if (!passwordRegex.test($signupPassword.val())) {
                let $errorDiv = $('<div class="alert alert-danger error-div">Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, one number, and one special character</div>');
                $modalBody.append($errorDiv);
            }
            // Validate email
            else if (!emailRegex.test($signupEmail.val())) {
                let $errorDiv = $('<div class="alert alert-danger error-div">Email does not appear to be valid</div>');
                $modalBody.append($errorDiv);
            }
            // Validate username & email are unique
            else {
                let response = await signupViaAxios();
                if (response['error']) {
                    signupReturnedErrorHandler(response);
                } else {
                    pageReload();
                }
            }
        });
    });

    afterEach(() => {
        // Clean up DOM elements
        $signupUsername.remove();
        $signupEmail.remove();
        $signupPassword.remove();
        $signupPassword2.remove();
        $signupButton.remove();
        $modalBody.remove();

        // Re-assign to correct functions
        // THIS CODE ISN'T WORKING
        window.signupViaAxios = signupViaAxios;
        window.signupReturnedErrorHandler = signupReturnedErrorHandler;
        window.pageReload = pageReload;


    });

    it('validates that all fields are required', async () => {
        $signupUsername.val('');
        $signupEmail.val('');
        $signupPassword.val('');
        $signupPassword2.val('');

        const event = $.Event('click');
        await $signupButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect($modalBody.find('.error-div').text()).toBe('Username, email, and password are required.');
        expect(signupViaAxiosSpy).not.toHaveBeenCalled();
        expect(signupReturnedErrorHandlerSpy).not.toHaveBeenCalled();
        expect(pageReloadSpy).not.toHaveBeenCalled();
    });

    it('validates that passwords match', async () => {
        $signupUsername.val('testuser15');
        $signupEmail.val('testuser@test.com');
        $signupPassword.val('password1!');
        $signupPassword2.val('password2!');

        const event = $.Event('click');
        await $signupButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect($modalBody.find('.error-div').text()).toBe('Passwords do not match.');
        expect(signupViaAxiosSpy).not.toHaveBeenCalled();
        expect(signupReturnedErrorHandlerSpy).not.toHaveBeenCalled();
        expect(pageReloadSpy).not.toHaveBeenCalled();
    });

    it('validates secure password', async () => {
        $signupUsername.val('testuser15');
        $signupEmail.val('testuser@test.com');
        $signupPassword.val('password'); // Not a secure password
        $signupPassword2.val('password');

        const event = $.Event('click');
        await $signupButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect($modalBody.find('.error-div').text()).toBe('Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, one number, and one special character');
        expect(signupViaAxiosSpy).not.toHaveBeenCalled();
        expect(signupReturnedErrorHandlerSpy).not.toHaveBeenCalled();
        expect(pageReloadSpy).not.toHaveBeenCalled();
    });

    it('validates email format', async () => {
        $signupUsername.val('testuser15');
        $signupEmail.val('invalid-email');
        $signupPassword.val('Password1!');
        $signupPassword2.val('Password1!');

        const event = $.Event('click');
        await $signupButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect($modalBody.find('.error-div').text()).toBe('Email does not appear to be valid');
        expect(signupViaAxiosSpy).not.toHaveBeenCalled();
        expect(signupReturnedErrorHandlerSpy).not.toHaveBeenCalled();
        expect(pageReloadSpy).not.toHaveBeenCalled();
    });

    it('calls signupViaAxios and handles the response when validation passes', async () => {
        $signupUsername.val('testuser15');
        $signupEmail.val('testuser@test.com');
        $signupPassword.val('Password1!');
        $signupPassword2.val('Password1!');

        const event = $.Event('click');
        await $signupButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(signupViaAxiosSpy).toHaveBeenCalled();
        expect(signupReturnedErrorHandlerSpy).not.toHaveBeenCalled();
        expect(pageReloadSpy).toHaveBeenCalled();
    });

    it('calls signupReturnedErrorHandler when signupViaAxios returns an error', async () => {
        $signupUsername.val('testuser15');
        $signupEmail.val('testuser@test.com');
        $signupPassword.val('Password1!');
        $signupPassword2.val('Password1!');

        // Mock signupViaAxios to return an error
        signupViaAxiosSpy.and.returnValue(Promise.resolve({ error: 'yes' }));

        const event = $.Event('click');
        await $signupButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(signupViaAxiosSpy).toHaveBeenCalled();
        expect(signupReturnedErrorHandlerSpy).toHaveBeenCalled();
        expect(pageReloadSpy).not.toHaveBeenCalled();
    });
});

describe('validation of login form', () => {
    let loginViaAxiosSpy, loginReturnedErrorHandlerSpy, pageReloadSpy;
    let $loginUsername, $loginPassword, $loginButton, $modalBody;
    beforeEach(() => {
        //create spies
        loginViaAxiosSpy = jasmine.createSpy('loginViaAxios');
        loginReturnedErrorHandlerSpy = jasmine.createSpy('loginReturnedErrorHandler');
        pageReloadSpy = jasmine.createSpy('pageReload');

        //assign spies to global scope
        window.loginViaAxios = loginViaAxiosSpy;
        window.loginReturnedErrorHandler = loginReturnedErrorHandlerSpy;
        window.pageReload = pageReloadSpy;

        //set up DOM
        $modalBody = $('<div class="modal-body"></div>').appendTo('body');
        $loginUsername = $('<input type="text" id="loginUsername">').appendTo('body');
        $loginPassword = $('<input type="text" id="loginPassword">').appendTo('body');
        $loginButton = $('<button id="loginButton">Login</button>').appendTo('body');

        //attach event handler to login button
        $loginButton.on('click', async function(event){
            event.preventDefault();
            $modalBody.find('.error-div').remove();
            //validate all data is present
            if ($loginUsername.val() === '' || $loginPassword.val()=== ''){
                let $errorDiv = $('<div class="alert alert-danger error-div">All fields are required.</div>');
                $modalBody.append($errorDiv);
            }
            else {
                let response = await loginViaAxios();
                if(response['error']){
                    loginReturnedErrorHandler(response);
                }
                else {
                    pageReload();
                }
            }
        });
    });

    afterEach(() => {
        //clean up DOM
        $modalBody.remove();
        $loginUsername.remove();
        $loginPassword.remove();
        $loginButton.remove();

        //reassign functions
        window.loginViaAxios = loginViaAxios;
        window.loginReturnedErrorHandler = loginReturnedErrorHandler;
        window.pageReload = pageReload;
    });

    it('validates correct data', async () => {
        $loginUsername.val('camdentadhg');
        $loginPassword.val('Password1!');

        // Mock loginViaAxios to return an error
        loginViaAxiosSpy.and.returnValue(Promise.resolve({}));

        const event = $.Event('click');
        await $loginButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(loginViaAxiosSpy).toHaveBeenCalled();
        expect(loginReturnedErrorHandlerSpy).not.toHaveBeenCalled();
        expect(pageReloadSpy).toHaveBeenCalled();
    });

    it('rejects missing data', async () => {
        $loginUsername.val('');
        $loginPassword.val('');

        const event = $.Event('click');
        await $loginButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(loginViaAxiosSpy).not.toHaveBeenCalled();
        expect(loginReturnedErrorHandlerSpy).not.toHaveBeenCalled();
        expect(pageReloadSpy).not.toHaveBeenCalled();
        expect($modalBody.find('.error-div').text()).toBe('All fields are required.');
    });

    it('calls error handler if error is returned', async () => {
        $loginUsername.val('camdentadhg');
        $loginPassword.val('diashwsohw');

        // Mock loginViaAxios to return an error
        loginViaAxiosSpy.and.returnValue(Promise.resolve({ error: 'yes' }));

        const event = $.Event('click');
        await $loginButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(loginViaAxiosSpy).toHaveBeenCalled();
        expect(loginReturnedErrorHandlerSpy).toHaveBeenCalled();
        expect(pageReloadSpy).not.toHaveBeenCalled();

    });
});

describe('send reminder event handler', () => {
    beforeEach(() => {
        //setup spies
        usernameReminderViaAxiosSpy = jasmine.createSpy('usernameReminderViaAxios');
        window.usernameReminderViaAxios = usernameReminderViaAxiosSpy;

        //set up DOM
        $modalBody = $('<div class="modalBody"></div>').appendTo('body');
        $sendreminderButton = $('<button id="send_reminder_button">Send username Reminder</button>')

        //attach event handler to button
        $sendreminderButton.on('click', async function(event){
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
        });
    });

    afterEach(() => {
        //clean up DOM
        $modalBody.remove();
        $sendreminderButton.remove();
    });

    it('returns correct message for invalid email', async () => {
        usernameReminderViaAxiosSpy.and.returnValue(Promise.resolve({error: 'yes'}));

        const event = $.Event('click')
        await $sendreminderButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(usernameReminderViaAxiosSpy).toHaveBeenCalled();
        expect($modalBody.find('.error-div')[0].innerText).toEqual('Email not in database. Please signup.');
        expect($modalBody.find('.error-div')[0].classList).toContain('alert-danger');
    });

    it('returns correct message for valid email', async () => {
        usernameReminderViaAxiosSpy.and.returnValue(Promise.resolve({success: true}));
        
        const event = $.Event('click');
        await $sendreminderButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(usernameReminderViaAxiosSpy).toHaveBeenCalled();
        expect($modalBody.find('.error-div')[0].innerText).toEqual('Email sent');
        expect($modalBody.find('.error-div')[0].classList).toContain('alert-success');
    })
});

describe('send reset event handler', () => {
    beforeEach(() => {
        //setup spies
        passwordResetViaAxiosSpy = jasmine.createSpy('passwordResetViaAxios');
        window.passwordResetViaAxios = passwordResetViaAxiosSpy;

        //set up DOM
        $modalBody = $('<div class="modalBody"></div>').appendTo('body');
        $sendResetButton = $('<button id="send_reset_button">Reset password</button>')

        //attach event handler to button
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
        });
    });

    afterEach(() => {
        //clean up DOM
        $modalBody.remove();
        $sendResetButton.remove();
    });

    it('returns correct message for invalid email', async () => {
        passwordResetViaAxiosSpy.and.returnValue(Promise.resolve({error: 'yes'}));

        const event = $.Event('click')
        await $sendResetButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(passwordResetViaAxiosSpy).toHaveBeenCalled();
        expect($modalBody.find('.error-div')[0].innerText).toEqual('Email not in database. Please signup.');
        expect($modalBody.find('.error-div')[0].classList).toContain('alert-danger');
    });

    it('returns correct message for valid email', async () => {
        passwordResetViaAxiosSpy.and.returnValue(Promise.resolve({success: true}));
        
        const event = $.Event('click');
        await $sendResetButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(passwordResetViaAxiosSpy).toHaveBeenCalled();
        expect($modalBody.find('.error-div')[0].innerText).toEqual('Email sent');
        expect($modalBody.find('.error-div')[0].classList).toContain('alert-success');
    })
});

describe('update password event handler', () => {
    let updatePasswordViaAxiosSpy;
    beforeEach(() => {
        //create spy
        updatePasswordViaAxiosSpy = jasmine.createSpy('updatePasswordViaAxios');
        window.updatePasswordViaAxios = updatePasswordViaAxiosSpy;

        //set up DOM
        $modalBody = $('<div class="modal-body"></div>').appendTo('body');
        $updatePasswordButton = $('<button class="update-password">Update Password</button>').appendTo('body');
        $updatePassword = $('<input type="text" id="update_password">').appendTo('body');
        $updatePassword2 = $('<input type="text" id="update_password2">').appendTo('body');

        //attach event handler to button
        $updatePasswordButton.on('click', async function(event){
            event.preventDefault();
            $modalBody.find('.error-div').remove();
            const passwordRegex = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$/;
            if ($updatePassword.val() !== $updatePassword2.val()){
                let $errorDiv = $('<div class="alert alert-danger error-div">Passwords do not match.</div>');
                $modalBody.append($errorDiv);
            }
            else if  (!passwordRegex.test($updatePassword.val())){
                let $errorDiv = $('<div class="alert alert-danger error-div">Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, one number, and one special character</div>');
                $modalBody.append($errorDiv);
            }
            else {
                let response = await updatePasswordViaAxios();
                if (response['error']){
                    let $errorDiv = $('<div class="alert alert-danger error-div">Something went wrong. Please try again</div>')
                    $modalBody.append($errorDiv);
                }
                if (response['success']){
                    let $errorDiv = $('<div class="alert alert-success error-div">Password updated</div>');
                    $modalBody.append($errorDiv);
                }
            }
        });
    });

    afterEach(() => {
        window.updatePasswordViaAxios = updatePasswordViaAxios;

        //clean up DOM
        $modalBody.remove();
        $updatePasswordButton.remove();
        $updatePassword.remove();
        $updatePassword2.remove();
    });

    it('rejects non-matching passwords', async () => {
        $updatePassword.val('Password1!!');
        $updatePassword2.val('Password1!');

        const event = $.Event('click');
        $updatePasswordButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(updatePasswordViaAxiosSpy).not.toHaveBeenCalled();
        expect($modalBody.find('.error-div')[0].innerText).toEqual('Passwords do not match.');
        expect($modalBody.find('.error-div')[0].classList).toContain('alert-danger');
    });

    it('rejects insecure passwords', () => {
        $updatePassword.val('password');
        $updatePassword2.val('password');

        const event = $.Event('click');
        $updatePasswordButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(updatePasswordViaAxiosSpy).not.toHaveBeenCalled();
        expect($modalBody.find('.error-div')[0].innerText).toEqual('Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, one number, and one special character');
        expect($modalBody.find('.error-div')[0].classList).toContain('alert-danger');
    });

    it('returns correct response if password is successfully updated', async () => {
        $updatePassword.val('Password1!');
        $updatePassword2.val('Password1!');
        updatePasswordViaAxiosSpy.and.returnValue(Promise.resolve({success: true}));

        const event = $.Event('click');
        await $updatePasswordButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(updatePasswordViaAxiosSpy).toHaveBeenCalled();
        expect($modalBody.find('.error-div')[0].innerText).toEqual('Password updated');
        expect($modalBody.find('.error-div')[0].classList).toContain('alert-success');
    });

    it('returns correct response if error is returned', async () => {
        $updatePassword.val('Password1!');
        $updatePassword2.val('Password1!');
        updatePasswordViaAxiosSpy.and.returnValue(Promise.resolve({error: true}));

        const event = $.Event('click');
        await $updatePasswordButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(updatePasswordViaAxiosSpy).toHaveBeenCalled();
        expect($modalBody.find('.error-div').text()).toEqual('Something went wrong. Please try again');
        expect($modalBody.find('.error-div')[0].classList).toContain('alert-danger');
    });
});