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
    # Function takes the triangle position and the current question
    # Iteration through the questions is done in the template

    # Things to note. A position is any point from 0 - 12 on a triangle.
    # A vertex is a labeled position on a triangle. There are only three
    # labeled positions aka vertices. 0, 1, or 2

    # Holds the number of times the normalized position is equal to the
    # traingle position
    num = 0

    ord_map = {}
    total = len(question.questionresponse_set.all())
    correct_marker = question.correct_marker()

    for qres in question.questionresponse_set.all():
        selected_pos = qres.selected_position

        # If selected position is 12 (I don't know), no need to normalize.
        if selected_pos == 12:
            if selected_pos == x:
                num += 1
            else:
                continue

        else:
            # Grab the correct Marker
            correct_qrm = qres.questionresponsemarker_set.get(
                          marker=correct_marker)
            # Get the incorrect Markers by asc order
            qfor = qres.questionresponsemarker_set.exclude(
                   marker=correct_marker).order_by('ordinal')
            # Create a normalized map where the correct marker is at ordinal 0
            # and the incorrect markers are 1 and 2 accoriding to the original
            # asc order.
            ord_map[correct_qrm] = 0
            ord_map[qfor.first()] = 1
            ord_map[qfor.last()] = 2

            # Based on selected position, find the previous vertex
            prev_vertex_ord = math.floor(selected_pos / 4)

            # Use the previous vertex to find the previous marker
            prev_marker = qres.questionresponsemarker_set.get(
                          ordinal=prev_vertex_ord)
            # Previous vertex position
            prev_vertex_pos = prev_vertex_ord * 4

            # Use the selected position and previous vertext position to
            # the offset between the selected pt and the closest vertex pt.
            offset = abs(selected_pos - prev_vertex_pos)

            # Using our normalized map, find where the previous marker is and
            # grab its normalized vertex. Then calculate the position.
            normalized_prev_vertex = ord_map[prev_marker]
            normalized_prev_pos = normalized_prev_vertex * 4
            normalized_position = offset + normalized_prev_pos

            # If x is equal to the normalized_position, add to the count
            if normalized_position == x:
                num += 1

    #  Calculate the percent
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


@register.simple_tag
def aria_label(x):

    labels = {
        0: 'This choice is A.',
        1: 'This choice is between A and B, close to A.',
        2: 'This choice is between A and B.',
        3: 'This choice is between A and B, close to B.',
        4: 'This choice is B.',
        5: 'This choice is between B and C, close to B.',
        6: 'This choice is between B and C.',
        7: 'This choice is between B and C, close to C.',
        8: 'This choice is C.',
        9: 'This choice is between C and A, close to C.',
        10: 'This choice is between C and A.',
        11: 'This choice is between C and A, close to A.',
        12: "This choice is I don't know."
    }

    return labels[x]
