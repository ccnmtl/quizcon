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
    if not submissions:
        return None

    max_points = submissions[0].user_points()
    for sub in submissions:
        if sub.user_points() > max_points:
            max_points = sub.user_points()
    return max_points


@register.simple_tag
def submission_min_points(submissions):
    if not submissions:
        return None

    min_points = submissions[0].user_points()
    for sub in submissions:
        if sub.user_points() < min_points:
            min_points = sub.user_points()
    return min_points


@register.simple_tag
def submission_median(submissions):
    points = []
    for sub in submissions:
        points.append(sub.user_points())
    try:
        median = statistics.median(points)
    except statistics.StatisticsError:
        median = "Cannot calculate median."
    return median


@register.simple_tag
def submission_mean(submissions):
    points = []
    for sub in submissions:
        points.append(sub.user_points())
    try:
        mean = round((statistics.mean(points)), 2)
    except statistics.StatisticsError:
        mean = "Cannot calculate mean."
    return mean


@register.simple_tag
def submission_mode(submissions):
    points = []
    for sub in submissions:
        points.append(sub.user_points())
    try:
        mode = round((statistics.mode(points)), 2)
    except statistics.StatisticsError:
        mode = "No unique mode."
    return mode


@register.simple_tag
def submission_standard_dev(submissions):
    points = []
    for sub in submissions:
        points.append(sub.user_points())
    try:
        stdev = round((statistics.stdev(points)), 2)
    except statistics.StatisticsError:
        stdev = "Not enough data"
    return stdev


def total_right_answers(question):
    num = 0
    for res in question.questionresponse_set.all():
        if res.is_correct():
            num += 1
    return num


def total_wrong_answers(question):
    num = 0
    for res in question.questionresponse_set.all():
        if not res.is_correct() and not res.selected_position == 12:
            num += 1
    return num


def total_idk_answers(question):
    num = 0
    for res in question.questionresponse_set.all():
        if res.selected_position == 12:
            num += 1
    return num


@register.simple_tag
def normalize_percent(qres):
    normalized_correct = 0
    selected_pos = qres.selected_position
    correct_pos = qres.correct_marker_position()
    distance = abs(selected_pos - correct_pos)
    normalized_selected = normalized_correct + distance

    return normalized_selected


@register.simple_tag
def percentage_choice(x, question):
    num = 0
    total = len(question.questionresponse_set.all())
    for res in question.questionresponse_set.all():
        normalized_percent = normalize_percent(res)
        if normalized_percent == x:
            num += 1

    if total > 0:
        percent = round((num / total * 100), 1)
    else:
        percent = 0
    return percent


@register.simple_tag
def questions_most_correct(id):
    quiz = Quiz.objects.get(pk=id)
    num_of_correct = {}
    for question in quiz.question_set.all():
        num_of_correct.update({question: total_right_answers(question)})
    max_num_correct = max(num_of_correct.values())

    if max_num_correct == 0:
        return []
    else:
        return [k for k, v in num_of_correct.items() if v == max_num_correct]


@register.simple_tag
def questions_most_incorrect(id):
    quiz = Quiz.objects.get(pk=id)
    num_of_incorrect = {}
    for question in quiz.question_set.all():
        num_of_incorrect.update({question: total_wrong_answers(question)})

    max_num_incorrect = max(num_of_incorrect.values())
    if max_num_incorrect == 0:
        return []
    else:
        return [k for k, v in num_of_incorrect.items()
                if v == max_num_incorrect]


@register.simple_tag
def questions_most_idk(id):
    quiz = Quiz.objects.get(pk=id)
    num_of_idk = {}
    for question in quiz.question_set.all():
        num_of_idk.update({question: total_idk_answers(question)})

    max_num_idk = max(num_of_idk.values())
    if max_num_idk == 0:
        return []
    else:
        return [k for k, v in num_of_idk.items() if v == max_num_idk]
