from django.urls import path

from .views import HomePageView, AboutPageView, PrivacyPolicyPageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("privacy-policy/", PrivacyPolicyPageView.as_view(), name="privacy_policy"),
]
