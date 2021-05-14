describe('Sign-In Stories', function() {
    beforeEach(() => {
        cy.visit('/accounts/logout/?next=/');
        cy.clearCookies();
    });

    it('Sign In', function() {
        // Navigate to the home page
        cy.visit('/');
        cy.title().should('equal', 'Quizzing With Confidence: Splash');
        cy.get('#cu-privacy-notice-button').click();
        cy.get('#login').should('exist');
        cy.get('#login').click();

        cy.title().should('equal', 'Quizzing With Confidence: Log in');
        cy.url().should('contain', '/accounts/login/?next=/');
        //cy.wait(500); // wait for jQuery to load

        cy.get('[data-cy="columbia-login"]').should('exist');
        cy.get('#guest-login').should('exist');

        // Sign in as a guest
        cy.get('#guest-login').click();

        cy.get('#id_username').should('be.visible');
        cy.get('#id_password').should('be.visible');
        cy.get('#guest-login-submit').should('be.visible');
        cy.get('#guest-login-error').should('not.exist');

        // Empty fields
        cy.get('#guest-login-submit').click();
        cy.get('#guest-login-error').should('be.visible');
        cy.get('#guest-login-error').should(
                'contain', 'Invalid username or password');

        // Invalid credentials
        cy.get('#id_username').type('faculty_one').blur();
        cy.get('#id_password').type('wrong').blur();
        cy.get('#guest-login-submit').click();
        cy.get('#guest-login-error').should('be.visible');
        cy.get('#guest-login-error').should(
                'contain', 'Invalid username or password');

        // Valid credentials
        cy.get('#id_username').type('faculty_one').blur();
        cy.get('#id_password').type('test').blur();
        cy.get('#guest-login-submit').click();

        // Navigate to the dashboard
        cy.title().should('equal', 'Quizzing With Confidence: Splash');
        cy.get('#login').should('not.exist');
        cy.get('#logout').should('exist');

        // Sign out
        cy.get('#logout').click();

        // Verify signed out state
        cy.title().should('equal', 'Quizzing With Confidence: Splash');
        cy.get('#login').should('exist');
    });
});
