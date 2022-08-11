from django import forms
from quizcon.main.models import Quiz, Question


class QuizForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scoring_scheme'].choices = [
            ('', '-- Select One --')] + list(
            self.fields['scoring_scheme'].choices[0:3])
        self.fields['scoring_scheme'].initial = '-- Select One --'

    class Meta:
        model = Quiz
        fields = ['title', 'description', 'multiple_attempts',
                  'show_answers', 'randomize', 'course', 'scoring_scheme',
                  'show_answers_date', 'time']
        labels = {
                    'title': '',
                    'description': '',
                    'scoring_scheme': '',
                    'multiple_attempts': '',
                    'show_answers': '',
                    'show_answers_date': '',
                    'time': '',
                    'randomize': ''
                }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'rows': 3,
                                          'placeholder': 'Description'}),
            'scoring_scheme': forms.Select(attrs={'class': 'form-select'}),
            'multiple_attempts': forms.NumberInput(
                                 attrs={'class': 'form-control'}),
            'show_answers': forms.RadioSelect(),
            'show_answers_date': forms.DateInput(
                                 attrs={
                                       'class': 'form-control',
                                       'type': 'date',
                                       'disabled': 'true',
                                       'aria-describedby': 'id_show_answers_2',
                                       'title': 'calendar'
                                      }),
            'time': forms.NumberInput(
                    attrs={'placeholder': 'Minutes', 'maxlength': '2'})
        }


class QuestionForm(forms.ModelForm):

    text = forms.CharField(
        required=False, widget=forms.Textarea(
            attrs={'rows': 2, 'placeholder': '', 'class': 'rich-text'}))

    answer_label_1 = forms.CharField(
        required=True, widget=forms.Textarea(
            attrs={'rows': 2, 'placeholder': 'First choice'}))
    answer_label_2 = forms.CharField(
        required=True, widget=forms.Textarea(
            attrs={'rows': 2, 'placeholder': 'Second choice'}))
    answer_label_3 = forms.CharField(
        required=True, widget=forms.Textarea(
            attrs={'rows': 2, 'placeholder': 'Third choice'}))

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
        labels = {
                    'quiz': '',
                    'text': '',
                    'explanation': ''
                }

        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': '',
                                          'class': 'rich-text'}),
            'explanation': forms.Textarea(attrs={'rows': 2, 'placeholder': '',
                                                 'class': 'rich-text',
                                                 'id': 'student-feedback'})
        }

    def clean_text(self):
        txt = self.cleaned_data.get('text', '')
        if txt is None or len(txt) < 1:
            self._errors['text'] = self.error_class([
                'Please enter question text'])
        return txt
