from django import template
from quizcon.main.models import Quiz
import statistics
import math

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
        if not res.is_correct() and not res.selected_position == 12:
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
    ord_map = {}
    num = 0
    total = len(question.questionresponse_set.all())
    # iterate thru q's in template
    correct_marker = question.correct_marker()
    for qres in question.questionresponse_set.all():
        correct_qrm = qres.questionresponsemarker_set.get(
                      marker=correct_marker)
        qfor = qres.questionresponsemarker_set.exclude(
               marker=correct_marker).order_by('ordinal')
        ord_map[correct_qrm] = 0
        ord_map[qfor.first()] = 1
        ord_map[qfor.last()] = 2

        selected_pos = qres.selected_position

        prev_vertex_ord = math.floor(selected_pos / 4)
        prev_marker = qres.questionresponsemarker_set.get(
                      ordinal=prev_vertex_ord)
        prev_vertex_pos = prev_vertex_ord * 4

        offset = abs(selected_pos - prev_vertex_pos)

        normalized_prev_vertex = ord_map[prev_marker]
        normalized_prev_pos = normalized_prev_vertex * 4
        normalized_position = offset + normalized_prev_pos

        if normalized_position == x:
            num += 1

    if total > 0:
        percent = round((num / total * 100), 1)
    else:
        percent = 0
    return percent


@register.simple_tag
def answers_pos(question):
    correct_marker = question.correct_marker()
    order_ans = {}
    qres = question.questionresponse_set.first()
    qresm = qres.questionresponsemarker_set.exclude(
           marker=correct_marker).order_by('ordinal')
    order_ans[1] = qresm.first().marker.label
    order_ans[2] = qresm.last().marker.label

    return order_ans
