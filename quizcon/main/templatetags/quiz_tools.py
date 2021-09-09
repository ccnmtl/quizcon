from django import template
from quizcon.main.models import Quiz
import statistics

register = template.Library()


@register.simple_tag
def question_response(question, submission):
    return submission.questionresponse_set.get(question=question)


@register.simple_tag
def radio_points(id, x):
    quiz = Quiz.objects.get(pk=id)
    value = quiz.value_per_marker(x)
    return value


@register.simple_tag
def submission_max_points(submissions):
    max_points = 0
    for sub in submissions:
        if sub.user_points() > max_points:
            max_points = sub.user_points()
    return max_points


@register.simple_tag
def submission_min_points(submissions):
    min_points = 0
    for sub in submissions:
        if sub.user_points() < min_points:
            min_points = sub.user_points()
    return min_points


@register.simple_tag
def submission_median(submissions):
    points = []
    for sub in submissions:
        points.append(sub.user_points())
    return statistics.median(points)


@register.simple_tag
def submission_mean(submissions):
    points = []
    for sub in submissions:
        points.append(sub.user_points())
    return round((statistics.mean(points)), 2)


@register.simple_tag
def submission_mode(submissions):
    points = []
    for sub in submissions:
        points.append(sub.user_points())
    return round((statistics.mode(points)), 2)


@register.simple_tag
def submission_standard_dev(submissions):
    points = []
    for sub in submissions:
        points.append(sub.user_points())
    return round((statistics.stdev(points)), 2)


@register.simple_tag
def total_right_answers(question):
    num = 0
    for res in question.questionresponse_set.all():
        if res.is_correct():
            num += 1
    return num


@register.simple_tag
def total_wrong_answers(question):
    num = 0
    for res in question.questionresponse_set.all():
        if not res.is_correct():
            num += 1
    return num


@register.simple_tag
def total_idk_answers(question):
    num = 0
    for res in question.questionresponse_set.all():
        if res.selected_position == 12:
            num += 1
    return num


@register.simple_tag
def percentage_choice(x, question):
    num = 0
    total = len(question.questionresponse_set.all())
    for res in question.questionresponse_set.all():
        if res.selected_position == x:
            num += 1

    return round((num / total * 100), 2)


@register.simple_tag
def right_answers_per_quiz(id):
    quiz = Quiz.objects.get(pk=id)
    num_of_correct = 0
    question_most_correct = None
    for question in quiz.question_set.all():
        if num_of_correct < total_right_answers(question):
            num_of_correct = total_right_answers(question)
            question_most_correct = question
    return question_most_correct


@register.simple_tag
def wrong_answers_per_quiz(id):
    quiz = Quiz.objects.get(pk=id)
    num_of_incorrect = 0
    question_least_correct = None
    for question in quiz.question_set.all():
        if num_of_incorrect < total_wrong_answers(question):
            num_of_incorrect = total_wrong_answers(question)
            question_least_correct = question
    return question_least_correct


@register.simple_tag
def idk_answers_per_quiz(id):
    quiz = Quiz.objects.get(pk=id)
    num_of_idk = 0
    question_most_idk = None
    for question in quiz.question_set.all():
        if num_of_idk < total_idk_answers(question):
            num_of_idk = total_idk_answers(question)
            question_most_idk = question
    return question_most_idk
