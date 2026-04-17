describe('Creating a quiz', function() {
    beforeEach(() => {
        cy.login('faculty_one', 'test');
        cy.get('[data-cy="course"] > a').click();
    });

    it('Should create a quiz', function() {
        cy.get('[data-cy="create-quiz"]').click();
        cy.title().should('equal', 'Quizzing With Confidence: Create Quiz');
        cy.get('[data-cy="create-quiz-form"]').should('contain', 'Create Quiz');
        cy.get('#id_title').type('Test Quiz');
        cy.get('#id_description').type('A test quiz.')
        cy.get('select').select('1');
        cy.get('form').submit();
    });
    it('Should show quiz on quizzes dashboard', function() {
        cy.get('[data-cy="Test Quiz"]').should('exist');
    });
    it('Tests a11y on my quizzes page', function() {
        cy.checkPageA11y();
    });
});
