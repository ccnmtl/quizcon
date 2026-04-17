describe('Sign-In Stories', function() {
    beforeEach(() => {
        cy.clearCookies();
        cy.clearLocalStorage();
        cy.visit('/');
    });

    it('Sign In', function() {
        // Navigate to the home page
        cy.title().should(
            'equal', 'Quizzing With Confidence: Sign In | QuizCon');
        cy.get('#cu-privacy-notice-button').click();
        cy.get('#cy-login').should('exist');
        cy.get('[data-cy="columbia-login"]').should('exist');
        cy.get('#guest-login').should('be.visible').click();

        cy.title().should('equal',
            'Quizzing With Confidence: Sign In | QuizCon');
        cy.url().should('contain', '/accounts/login/?next=/');
        //cy.wait(500); // wait for jQuery to load

        cy.get('form').should('have.length.at.least', 1);
        cy.get('input[name="csrfmiddlewaretoken"]').should('exist');

        // Sign in as a guest
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
        cy.get('#id_username').clear().type('faculty_one').blur();
        cy.get('#id_password').clear().type('wrong').blur();
        cy.get('#guest-login-submit').click();
        cy.get('#guest-login-error').should('be.visible');
        cy.get('#guest-login-error').should(
            'contain', 'Invalid username or password');

        // Valid credentials

        cy.get('#id_username').clear().type('faculty_one').blur();
        cy.get('#id_password').clear().type('test').blur();
        cy.get('#guest-login-submit').click();

        // Navigate to the dashboard
        cy.title().should(
            'equal', 'Quizzing With Confidence: My Courses | QuizCon');
        cy.get('#cy-login').should('not.exist');
        cy.get('#logout').should('exist');

        // Sign out
        cy.get('form[action*="/accounts/logout/"]').within(() => {
            cy.get('input[name="csrfmiddlewaretoken"]').should('exist');
            cy.get('button[type="submit"], input[type="submit"]').click();
        });

        // Verify signed out state
        cy.title().should(
            'equal', 'Quizzing With Confidence: Sign In | QuizCon');
        cy.get('#cy-login').should('exist');
    });
    it('Tests a11y on login page', function() {
        cy.checkPageA11y();
    });
});
