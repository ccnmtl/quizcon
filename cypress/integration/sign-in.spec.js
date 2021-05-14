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
        cy.get('[data-cy="login-small"]').should('exist');
        cy.get('[data-cy="login-small"]').click();

        cy.title().should('equal', 'Quizzing With Confidence: Log in');
        cy.url().should('contain', '/accounts/login/?next=/');
        // cy.wait(500); // wait for jQuery to load

        cy.get('[data-cy="columbia-login"]').should('exist');
        cy.get('[data-cy="guest-login"]').should('exist');

        // Sign in as a guest
        cy.get('[data-cy="guest-login"]').click();

        cy.get('[data-cy="guest-login-username"]').should('be.visible');
        cy.get('[data-cy="guest-login-password"]').should('be.visible');
        cy.get('[data-cy="guest-login-submit"]').should('be.visible');
        cy.get('[data-cy="guest-login-error"]').should('not.exist');

        // Empty fields
        cy.get('[data-cy="guest-login-submit"]').click();
        cy.get('[data-cy="guest-login-error"]').should('be.visible');
        cy.get('[data-cy="guest-login-error"]').should(
                'contain', 'Invalid username or password');

        // Invalid credentials
        cy.get('[data-cy="guest-login-username"]').type('faculty_one').blur();
        cy.get('[data-cy="guest-login-password"]').type('wrong').blur();
        cy.get('[data-cy="guest-login-submit"]').click();
        cy.get('[data-cy="guest-login-error"]').should('be.visible');
        cy.get('[data-cy="guest-login-error"]').should(
                'contain', 'Invalid username or password');

        // Valid credentials
        cy.get('[data-cy="guest-login-username"]').type('faculty_one').blur();
        cy.get('[data-cy="guest-login-password"]').type('test').blur();
        cy.get('[data-cy="guest-login-submit"]').click();

        // Navigate to the dashboard
        cy.title().should('equal', 'Quizzing With Confidence: Splash');
        cy.get('[data-cy="login-small"]').should('not.exist');
        cy.get('[data-cy="logout-small"]').should('exist');

        // Sign out
        cy.get('[data-cy="logout-small"]').click();

        // Verify signed out state
        cy.title().should('equal', 'Log in | DESIGN Online');
        cy.get('[data-cy="login-small"]').should('exist');
    });
});
