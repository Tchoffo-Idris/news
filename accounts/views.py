from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.contrib.auth import logout

from .forms import CustomUserCreationForm


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("home")
    template_name = "registration/signup.html"


@method_decorator(login_required, name='dispatch')
class LogoutConfirmView(TemplateView):
    template_name = "registration/logout_confirm.html"
    
    def post(self, request, *args, **kwargs):
        # User confirmed logout
        logout(request)
        return HttpResponseRedirect(reverse_lazy("home"))
    
    def get(self, request, *args, **kwargs):
        # Show confirmation page
        return super().get(request, *args, **kwargs)
