describe('Editing a question', function() {
    beforeEach(() => {
        cy.login('faculty_one', 'test');
        cy.get('[data-cy="course"] > a').click();
    });

    it('Should create a question', function() {
        cy.get('[data-cy="edit-A Bird Quiz"]').click();
        cy.get('[data-cy="edit-btn-What kind of bird has a huge yellow bill?"]')
            .click();
        cy.title().should('equal', 'Quizzing With Confidence: Edit Question');
        cy.get('[data-cy="question-text"]').find('iframe')
            .its('0.contentDocument').should('exist')
            .its('body').should('not.be.undefined')
            .then(cy.wrap).clear().click()
            .type('What is the only type of bird that can fly backwards?');
        cy.get('[data-cy="student-feedback"]').find('iframe')
            .its('0.contentDocument').should('exist')
            .its('body').should('not.be.undefined')
            .then(cy.wrap).clear().click()
            .type('The answer is hummingbird.');
        cy.get('#id_answer_label_1').clear().type('Hummingbird');
        cy.get('#id_answer_label_2').clear().type('Chicken');
        cy.get('#id_answer_label_3').clear().type('Eagle');
        cy.get('#answer-label-one').click();
        cy.get('[data-cy="save-question-btn"]').click();
    });
    it('Should show question on quiz edit page', function() {
        cy.get('[data-cy="edit-A Bird Quiz"]').click();
        cy.get(
            '[data-cy="What is the only type of bird that can fly backwards?"]')
            .should('exist');
    });
});
