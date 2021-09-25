from django.contrib import admin
from django.urls import path

from cognito_auth_playground.apps.core import views
from cognito_auth_playground.apps.core.api import api_views
from cognito_auth_playground.apps.core.api.v1 import api_views as api_views_v1

urlpatterns = [
    # Pages
    path("", views.index, name="index"),
    path("login-auth-code", views.initiate_login_flow, name="login-auth-code-flow"),
    path("logout", views.logout, name="logout"),
    # APIs
    path("health-check", api_views.health_check, name="health-check"),
    path("api/v1/response-oidc", api_views_v1.handle_response_oidc, name="v1/response-oidc"),
]
