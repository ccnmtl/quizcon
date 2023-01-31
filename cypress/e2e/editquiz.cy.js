describe('Creating a quiz', function() {
    beforeEach(() => {
        cy.login('faculty_one', 'test');
        cy.get('[data-cy="course"] > a').click();
    });

    it('Should edit a quiz', function() {
        cy.get('[data-cy="edit-A Bird Quiz"]').click();
        cy.title().should('equal', 'Quizzing With Confidence: Edit Quiz');
        cy.get('#id_description').clear().type('A quiz about birds.');
        cy.get('select').select('1');
        cy.get('#id_show_answers_0').click();
        cy.get('[data-cy="save-quiz-btn"]').click();
    });
    it('Should show edited quiz on quizzes dashboard', function() {
        cy.get('[data-cy="A Bird Quiz"]').should('exist');
        cy.get('[data-cy="A quiz about birds."]').should('exist');
    });
});
