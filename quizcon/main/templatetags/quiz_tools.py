from django import template
from quizcon.main.models import Quiz

register = template.Library()


@register.simple_tag
def question_response(question, submission):
    return submission.questionresponse_set.get(question=question)


@register.simple_tag
def radio_points(id, x):
    quiz = Quiz.objects.get(pk=id)
    value = quiz.value_per_marker(x)
    return value
