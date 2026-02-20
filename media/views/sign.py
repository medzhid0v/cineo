from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import FormView

from media.forms import SignUpForm
from media.usecases.signup import SignUpInput, SignUpUsecase


class SignUpView(FormView):
    template_name = "auth/signup.html"
    form_class = SignUpForm

    def form_valid(self, form):
        usecase = SignUpUsecase()
        user = usecase.execute(
            SignUpInput(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
        )
        login(self.request, user)
        return redirect("media:list")
