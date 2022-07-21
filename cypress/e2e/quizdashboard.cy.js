describe('Quizzes dashboard', function() {
    before(() => {
        cy.login('faculty_one', 'test');
    });

    it('Quizzes dashboard', function() {
        cy.get('[data-cy="course"] > a').click();
        cy.title().should(
            'equal', 'Quizzing With Confidence: course 0');
        cy.get('[data-cy="create-quiz"]').should('exist');
    });
    it('Tests a11y on login page', function() {
        cy.checkPageA11y();
    });

});
