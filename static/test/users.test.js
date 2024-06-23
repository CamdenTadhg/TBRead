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
        signupViaAxiosSpy.and.returnValue(Promise.resolve({ error: true }));

        const event = $.Event('click');
        await $signupButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(signupViaAxiosSpy).toHaveBeenCalled();
        expect(signupReturnedErrorHandlerSpy).toHaveBeenCalled();
        expect(pageReloadSpy).not.toHaveBeenCalled();
    });
});

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
        console.log(response);
        signupReturnedErrorHandler(response);
        expect($modalBody.find('.error-div').text()).toBe('Email already registered. Please try logging in.');
    });

    it('returns correct error message for duplicate username error', () => {
        const response = {error: 'Username already taken'};
        console.log(response);
        signupReturnedErrorHandler(response);
        expect($modalBody.find('.error-div').text()).toBe('Username already registered. Please try logging in.');
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
        console.log('running validates correct data');
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
        console.log('running rejects missing data');
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
        console.log('running calls error handler');
        $loginUsername.val('camdentadhg');
        $loginPassword.val('diashwsohw');

        // Mock loginViaAxios to return an error
        loginViaAxiosSpy.and.returnValue(Promise.resolve({ error: true }));

        const event = $.Event('click');
        await $loginButton.trigger(event);

        expect(event.isDefaultPrevented()).toBe(true);
        expect(loginViaAxiosSpy).toHaveBeenCalled();
        expect(loginReturnedErrorHandlerSpy).toHaveBeenCalled();
        expect(pageReloadSpy).not.toHaveBeenCalled();
    });
});