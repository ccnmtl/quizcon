from django import forms
from quizcon.main.models import Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'multiple_attempts',
                  'show_answers', 'randomize', 'course', 'scoring_scheme']

        widgets = {
            'title': forms.TextInput(),
            'description': forms.Textarea(attrs={'rows': 3})
        }
