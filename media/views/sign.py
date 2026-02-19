from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import FormView

from media.forms import SignUpForm


class SignUpView(FormView):
    template_name = "auth/signup.html"
    form_class = SignUpForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("media:list")
