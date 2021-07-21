from django import template
register = template.Library()


@register.simple_tag
def question_response(question, submission):
    return submission.questionresponse_set.get(question=question)
