describe('Sign-In Stories', function() {
    beforeEach(() => {
        cy.visit('/accounts/logout/?next=/');
        cy.clearCookies();
    });

    it('Sign In', function() {
        // Navigate to the home page
        cy.title().should(
            'equal', 'Quizzing With Confidence: Sign In | QuizCon');
        cy.get('#cu-privacy-notice-button').click();
        cy.get('#cy-login').should('exist');
        cy.get('[data-cy="columbia-login"]').should('exist');
        cy.get('#guest-login').should('exist');
        cy.get('#guest-login').click();

        cy.title().should('equal',
            'Quizzing With Confidence: Sign In | QuizCon');
        cy.url().should('contain', '/accounts/login/?next=/');
        //cy.wait(500); // wait for jQuery to load

        // Sign in as a guest
        cy.get('#guest-login').click({force: true});

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
        cy.get('#guest-login-submit').click({force: true});
        cy.get('#guest-login-error').should('be.visible');
        cy.get('#guest-login-error').should(
            'contain', 'Invalid username or password');

        // Valid credentials
        cy.get('#id_username').type('faculty_one').blur();
        cy.get('#id_password').type('test').blur();
        cy.get('#guest-login-submit').click({force: true});

        // Navigate to the dashboard
        cy.title().should(
            'equal', 'Quizzing With Confidence: My Courses | QuizCon');
        cy.get('#cy-login').should('not.exist');
        cy.get('#logout').should('exist');

        // Sign out
        cy.get('#logout').click({force: true});

        // Verify signed out state
        cy.title().should(
            'equal', 'Quizzing With Confidence: Sign In | QuizCon');
        cy.get('#cy-login').should('exist');
    });
    it('Tests a11y on login page', function() {
        cy.checkPageA11y();
    });
});
