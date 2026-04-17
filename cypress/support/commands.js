// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
Cypress.Commands.add('login', (username, password) => {
    cy.visit('/accounts/logout/?next=/');
    cy.get('#guest-login').click();
    cy.get('#id_username').type(username).blur();
    cy.get('#id_password').type(password).blur();
    cy.get('#guest-login-submit').click({force: true});
});

// Lifted this pattern from https://github.com/jonoliver/cypress-axe-demo

const severityIndicators = {
    minor: '⚪️',
    moderate: '🟡',
    serious: '🟠',
    critical: '🔴',
};

function callback(violations) {
    violations.forEach(violation => {
        const nodes =
              Cypress.$(violation.nodes.map(node => node.target).join(','));

        Cypress.log({
            name: `${severityIndicators[violation.impact]} A11Y`,
            consoleProps: () => violation,
            $el: nodes,
            message: `[${violation.help}](${violation.helpUrl})`
        });
        violation.nodes.forEach(({ target }) => {
            Cypress.log({
                name: '🔧',
                consoleProps: () => violation,
                $el: Cypress.$(target.join(',')),
                message: target
            });
        });
    });
}

Cypress.Commands.add('checkPageA11y', () => {
    cy.injectAxe();

    const ctx = {runOnly: {type: 'tag', values: ['wcag2a']}};
    cy.checkA11y('html', ctx, callback);
});
