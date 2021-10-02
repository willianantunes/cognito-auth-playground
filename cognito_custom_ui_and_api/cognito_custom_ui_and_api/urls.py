from django.contrib import admin
from django.urls import path

from cognito_custom_ui_and_api.apps.core import views
from cognito_custom_ui_and_api.apps.core.api import api_views
from cognito_custom_ui_and_api.apps.core.api.v1 import api_views as api_views_v1

urlpatterns = [
    # Pages
    path("", views.index, name="index"),
    path("login-auth-code", views.initiate_login_flow, name="login-auth-code-flow"),
    path("logout", views.logout, name="logout"),
    # APIs
    path("health-check", api_views.health_check, name="health-check"),
    path("api/v1/response-oidc", api_views_v1.handle_response_oidc, name="v1/response-oidc"),
    path("api/v1/user-info", api_views_v1.retrieve_user_info, name="v1/user-info"),
]
