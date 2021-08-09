from django import forms
from quizcon.main.models import Quiz, Question


class QuizForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scoring_scheme'].choices = [
            ('', '-- Select One --')] + list(
            self.fields['scoring_scheme'].choices[0:])
        self.fields['scoring_scheme'].initial = '-- Select One --'

    class Meta:
        model = Quiz
        fields = ['title', 'description', 'multiple_attempts',
                  'show_answers', 'randomize', 'course', 'scoring_scheme',
                  'show_answers_date']

        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(attrs={'rows': 3}),
            'scoring_scheme': forms.Select(attrs={'class': 'form-select'}),
            'multiple_attempts': forms.NumberInput(
                                 attrs={'class': 'form-control'}),
            'show_answers': forms.RadioSelect(),
            'show_answers_date': forms.DateInput(
                                attrs={'class': 'form-control',
                                       'type': 'date'})
        }


class QuestionForm(forms.ModelForm):

    answer_label_1 = forms.CharField(
        required=True, widget=forms.Textarea(
                                    attrs={'rows': 2, 'placeholder': ''}))
    answer_label_2 = forms.CharField(
        required=True, widget=forms.Textarea(
                                    attrs={'rows': 2, 'placeholder': ''}))
    answer_label_3 = forms.CharField(
        required=True, widget=forms.Textarea(
                                    attrs={'rows': 2, 'placeholder': ''}))

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
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': ''}),
            'explanation': forms.Textarea(attrs={'rows': 2, 'placeholder': ''})
        }
