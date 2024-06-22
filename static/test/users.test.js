describe('validation of signup form', () => { 
    let $signupButton, $modalBody, $signupPassword, signupPassword2, signupViaAxiosSpy, signupReturnedErrorHandlerSpy;
    beforeEach(() => {
        $signupUsername = $('<input id="signup_username" type="text">');
        $signupEmail=$('<input id="singup_email" type="text">');
        $signupPassword = $('<input id="singup_password" type="password">');
        $signupPassword2 = $('<input id="password2" type="password>"')
        $signupButton = $('<button id="signup-button>Sign up</button>"');
        $modalBody = $('<div id="modal-body></div>');
        signupViaAxiosSpy = jasmine.createSpy('signupViaAxios');
        signupReturnedErrorHandlerSpy = jasmine.createSpy('signupReturnedErrorHandler');
        preventDefault = jasmine.createSpy('preventDefault');

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
                let $errorDiv = $('<div class="alert alert-danger error-div">Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, one number, and one special character</div>');
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
    });

    it('validates correct information', async () => {
        $signupUsername.val('testuser');
        $signupEmail.val('testuser@test.com');
        $signupPassword.val('eQcBH9c%%h8QT8gM');
        $signupPassword2.val('eQcBH9c%%h8QT8gM');
        spyOn(window.location, 'reload');
        $signupButton.triggerHandler('click');
        expect(preventDefault).toHaveBeenCalledTimes(1);
        expect(signupViaAxiosSpy).toHaveBeenCalledTimes(1);
        expect(window.location.reload).toHaveBeenCalledTimes(1);
    });

    it('rejects non matching passwords', () =>{
        $signupUsername.val('testuser');
        $signupEmail.val('testuser@test.com');
        $signupPassword.val('eQcBh9c%%h8QT8gm');
        $signupPassword2.val('eQcBh0c%%h8QT8gm');
        spyOn(window.location, 'reload');
        $signupButton.trigger('click');
        expect(preventDefault).toHaveBeenCalledTimes(1);
        expect(signupViaAxiosSpy).toHaveBeenCalledTimes(0);
        expect(window.location.reload).toHaveBeenCalledTimes(0);
        expect($modalBody.find('.error-div').text()).toBe('Passwords do not match. Please try again');
    });
    
    it('rejects insecure passwords', () => {
        $signupUsername.val('testuser');
        $signupEmail.val('testuser@test.com');
        $signupPassword.val('password');
        $signupPassword2.val('password');
        spyOn(window.location, 'reload');
        $signupButton.trigger('click');
        expect(preventDefault).toHaveBeenCalledTimes(1);
        expect(signupViaAxiosSpy).toHaveBeenCalledTimes(0);
        expect(window.location.reload).toHaveBeenCalledTimes(0);
        expect($modalBody.find('.error-div').text()).toBe('Password must be at least 8 characters and contain one uppercase letter, one lowercase letter, and one number');
    });

    it('rejects missing data', () => {
    });
    it('rejects invalid email', () => {});
});
