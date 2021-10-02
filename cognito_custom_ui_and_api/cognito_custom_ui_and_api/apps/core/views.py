import logging
import uuid

from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from cognito_custom_ui_and_api.apps.core.services.cognito_user_pool import CognitoUserPool
from cognito_custom_ui_and_api.settings import AWS_COGNITO_APP_CLIENT_ID
from cognito_custom_ui_and_api.settings import AWS_COGNITO_APP_SCOPES

logger = logging.getLogger(__name__)


def index(request):
    logged_user = request.session.get("user")
    context = {}

    if logged_user:
        logout_request_path = reverse("logout")
        logout_uri = request.build_absolute_uri(logout_request_path)
        final_logout_uri = CognitoUserPool.build_logout_url(AWS_COGNITO_APP_CLIENT_ID, logout_uri)
        # TODO: Enrich logged area with data
        context["logout_uri"] = final_logout_uri

    return render(request, "core/pages/home.html", context)


def logout(request):
    request.session.flush()
    index_request_path = reverse("index")
    redirect_uri = request.build_absolute_uri(index_request_path)
    redirect_uri = redirect_uri.replace("http", "https") if "localhost" not in redirect_uri else redirect_uri
    return redirect(redirect_uri)


def initiate_login_flow(request):
    redirect_uri = _build_redirect_uri(request)
    logger.info("Building flow session details...")
    some_state = str(uuid.uuid4())
    flow_details = {
        "client_id": AWS_COGNITO_APP_CLIENT_ID,
        "scopes": AWS_COGNITO_APP_SCOPES,
        "state": some_state,
        "redirect_uri": redirect_uri,
    }
    # So we can retrieve it later
    request.session["flow"] = flow_details
    # Then we redirect the user
    auth_uri = CognitoUserPool.build_authorization_url(
        flow_details["client_id"], "code", flow_details["scopes"], redirect_uri, some_state
    )
    return redirect(auth_uri)


def _build_redirect_uri(request):
    location_redirect = reverse("v1/response-oidc")
    redirect_uri = request.build_absolute_uri(location_redirect)
    return redirect_uri.replace("http", "https") if "localhost" not in redirect_uri else redirect_uri
