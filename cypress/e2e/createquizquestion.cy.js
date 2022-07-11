describe('Creating a question', function() {
    before(() => {
        cy.login('faculty_one', 'test');
        cy.get('[data-cy="course"] > a').click();
    });

    it('Should create a question', function() {
        cy.get('[data-cy="A Bird Quiz"]').click();
        cy.get('[data-cy="edit-A Bird Quiz"]').click();
        cy.get('[data-cy="create-question"]').click();
        cy.title().should('equal', 'Quizzing With Confidence: Create Question');
        cy.get('[data-cy="question-text"]').find('iframe')
                .its('0.contentDocument').should('exist')
                .its('body').should('not.be.undefined')
                .then(cy.wrap).click().type('What kind of bird has a huge yellow bill?');
        cy.get('[data-cy="student-feedback"]').find('iframe')
                .its('0.contentDocument').should('exist')
                .its('body').should('not.be.undefined')
                .then(cy.wrap).click().type('The answer is toucan.');
        cy.get('#id_answer_label_1').type('Ibis');
        cy.get('#id_answer_label_2').type('Toucan');
        cy.get('#id_answer_label_3').type('Puffin');
        cy.get('#answer-label-two').click();
        cy.get('form').submit();
    });
    it('Should show question on quiz edit page', function() {
        cy.get('[data-cy="What kind of bird has a huge yellow bill?"]').should('exist');
    });
    it('Tests a11y on quiz edit page', function() {
       cy.checkPageA11y();
    });
});
