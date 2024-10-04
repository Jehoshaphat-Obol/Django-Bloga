from django.urls import path
from . import views

app_name = "authentication"

# Authentication url definitions
urlpatterns = [
    path("", views.sign_in_view, name="sign_in"),
    path("sign-up/", views.sign_up_view, name="sign_up"),
    path("sign-out/", views.sign_out_view, name="sign_out"),
]