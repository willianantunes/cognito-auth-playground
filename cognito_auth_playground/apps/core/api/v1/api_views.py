import logging

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from cognito_auth_playground.apps.core.api.api_exception import ContractNotRespectedException
from cognito_auth_playground.apps.core.services.cognito_user_pool import CognitoUserPool
from cognito_auth_playground.settings import AWS_COGNITO_APP_CLIENT_ID
from cognito_auth_playground.settings import AWS_COGNITO_APP_CLIENT_SECRET
from cognito_auth_playground.settings import AWS_COGNITO_APP_SCOPES

logger = logging.getLogger(__name__)


@api_view(["GET"])
def handle_response_oidc(request: Request) -> Response:
    # Sample incoming request: http://localhost:8000/api/v1/response-oidc?code=8ddbdc82-cb95-4bc8-b581-d001579045a6&state=f5787e3d-0b5e-4860-84b0-778e7c7a1a68
    current_referer = request.headers.get("referer")
    logger.info("Handling callback! It came from %s", current_referer)

    auth_flow_details = request.session.pop("flow", {})
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code or not state or not auth_flow_details:
        raise ContractNotRespectedException
    if auth_flow_details["state"] != state:
        raise ContractNotRespectedException

    logger.info("We have everything to contact token endpoint!")
    tokens, claims = CognitoUserPool.acquire_token_by_auth_code_flow(
        auth_flow_details["client_id"],
        AWS_COGNITO_APP_CLIENT_SECRET,
        code,
        auth_flow_details["scopes"],
        auth_flow_details["redirect_uri"],
    )

    request.session["user"] = claims
    request.session["tokens"] = tokens
    location_index = reverse("index")
    return redirect(location_index)
