from django import forms

from media.models import UserTitleState


class UpdateUserTitleStateForm(forms.ModelForm):
    rating = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={"class": "input", "min": 0, "max": 10}),
    )

    class Meta:
        model = UserTitleState
        fields = ("status", "rating", "review", "started_at", "finished_at")
        widgets = {
            "status": forms.Select(attrs={"class": "input"}),
            "rating": forms.NumberInput(attrs={"class": "input", "min": 0, "max": 10}),
            "review": forms.Textarea(attrs={"class": "input", "rows": 5, "placeholder": "Ваш отзыв"}),
            "started_at": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "finished_at": forms.DateInput(attrs={"class": "input", "type": "date"}),
        }
