from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from media.models import UserTitleState


class KinopoiskImportForm(forms.Form):
    kp_id = forms.IntegerField(
        label="КиноПоиск ID",
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "input", "placeholder": "Например: 301"}),
    )


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"


class UserTitleStateForm(forms.ModelForm):
    class Meta:
        model = UserTitleState
        fields = ("status", "rating", "review")
        widgets = {
            "status": forms.Select(attrs={"class": "input"}),
            "rating": forms.NumberInput(attrs={"class": "input", "min": 0, "max": 10}),
            "review": forms.Textarea(attrs={"class": "input", "rows": 5, "placeholder": "Ваш отзыв"}),
        }
