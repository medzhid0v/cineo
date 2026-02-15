from django import forms


class KinopoiskImportForm(forms.Form):
    kp_id = forms.IntegerField(
        label="КиноПоиск ID",
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "input", "placeholder": "Например: 301"}
        ),
    )
