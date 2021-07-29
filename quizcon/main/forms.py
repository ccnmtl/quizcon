from django import forms
from quizcon.main.models import Quiz, Question


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'multiple_attempts',
                  'show_answers', 'randomize', 'course', 'scoring_scheme']

        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(attrs={'rows': 3})
        }


class QuestionForm(forms.ModelForm):

    answer_label_1 = forms.CharField(
        required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
    answer_label_2 = forms.CharField(
        required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
    answer_label_3 = forms.CharField(
        required=True, widget=forms.TextInput(attrs={'class': "form-control"}))

    correct = forms.IntegerField(required=True)

    def __init__(self, *args, **kwargs):

        if kwargs.get('instance'):
            question = kwargs.get('instance')
            markers = question.marker_set.all().order_by('pk')

            initial = kwargs.setdefault('initial', {})
            for idx, marker in enumerate(markers):
                initial['answer_label_' + str(idx + 1)] = marker.label
                if marker.correct:
                    initial['correct'] = idx + 1

            kwargs.update({'initial': initial})
        super(QuestionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Question
        fields = ['quiz', 'text', 'explanation']

        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(attrs={'rows': 3})
        }
