describe('Courses dashboard', function() {
    beforeEach(() => {
        cy.login('faculty_one', 'test');
    });

    it('Courses dashboard', function() {
        cy.title().should(
            'equal', 'Quizzing With Confidence: My Courses | QuizCon');
        cy.get('[data-cy="course"]').should('exist');
        cy.get('[data-cy="dashboard-title"]').should('contain', 'My Courses');
        cy.get('[data-cy="course"] > a').click();
    });
    it('Tests a11y on Courses dashboard', function() {
        cy.checkPageA11y();
    });

});
