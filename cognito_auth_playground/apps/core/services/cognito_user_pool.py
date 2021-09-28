import logging

from base64 import b64encode
from dataclasses import asdict
from dataclasses import dataclass
from typing import List
from typing import Tuple
from typing import TypedDict
from urllib import parse

import requests

from jose import JWTError
from jose import jwk
from jose import jwt
from jose.utils import base64url_decode

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OIDCConfigurationDocument:
    # Endpoints
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    # Metadata
    id_token_signing_alg_values_supported: List[str]
    issuer: str
    jwks_uri: str
    response_types_supported: List[str]
    scopes_supported: List[str]
    subject_types_supported: List[str]
    token_endpoint_auth_methods_supported: List[str]
    # Custom fields made by me
    logout_endpoint: str
    revoke_endpoint: str


@dataclass(frozen=True)
class JWTPublicKey:
    alg: str
    e: str
    kid: str
    kty: str
    n: str
    use: str


class TokensBoundToSomeUser(TypedDict):
    id_token: str
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str


class Claims(TypedDict):
    pass


class CognitoUserPool:
    oidc_configuration_document: OIDCConfigurationDocument
    jwt_public_keys: List[JWTPublicKey]

    @classmethod
    def configure_oidc_configuration_document(cls, url: str):
        standard_time_out = (2, 5)
        document = requests.get(url, timeout=standard_time_out).json()

        # First let's configure the OIDC configuration document
        base_endpoint = document["token_endpoint"].split("/oauth2/token")[0]
        document["logout_endpoint"] = f"{base_endpoint}/logout"
        document["revoke_endpoint"] = f"{base_endpoint}/revoke"
        cls.oidc_configuration_document = OIDCConfigurationDocument(**document)

        # Now the public keys to verify the JWT created by Cognito
        public_keys = requests.get(cls.oidc_configuration_document.jwks_uri, timeout=standard_time_out).json()
        jwt_public_keys = []
        for public_key in public_keys["keys"]:
            jwt_public_key = JWTPublicKey(**public_key)
            jwt_public_keys.append(jwt_public_key)
        cls.jwt_public_keys = jwt_public_keys

    @classmethod
    def retrieve_claims_otherwise_raise_exception_if_token_is_invalid(cls, token: str) -> dict:
        logger.debug("Verifying if token is valid: %s", token)

        headers = jwt.get_unverified_headers(token)
        # Key Identifier is used to specify the key for validating the signature
        # https://datatracker.ietf.org/doc/html/rfc7515#section-4.1.4
        kid = headers["kid"]
        found_key = None
        for public_key in cls.jwt_public_keys:
            if public_key.kid == kid:
                found_key = public_key

        key_not_available = not found_key
        if key_not_available:
            raise JWTError

        logger.debug("Building public key...")
        constructed_public_key = jwk.construct(asdict(found_key))
        # Get the last two sections of the token,
        message, encoded_signature = str(token).rsplit(".", 1)
        logger.debug("Steps to verify the signature...")
        decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))
        is_valid_signature = constructed_public_key.verify(message.encode("utf8"), decoded_signature)
        if not is_valid_signature:
            raise JWTError

        logger.debug("Now we can get the claim without worries 😃")
        return jwt.get_unverified_claims(token)

    @classmethod
    def build_logout_url(cls, client_id, logout_uri):
        # https://docs.aws.amazon.com/cognito/latest/developerguide/logout-endpoint.html
        logout_url = cls.oidc_configuration_document.logout_endpoint
        params = {"client_id": client_id, "logout_uri": logout_uri}

        logger.debug("Building final URL...")
        url_parse = parse.urlparse(logout_url)
        query = url_parse.query
        url_dict = dict(parse.parse_qsl(query))
        url_dict.update(params)
        url_new_query = parse.urlencode(url_dict)
        url_parse = url_parse._replace(query=url_new_query)
        final_url = parse.urlunparse(url_parse)

        logger.debug("URL which has been built: %s", final_url)
        return final_url

    @classmethod
    def build_authorization_url(
        cls, client_id: str, response_type: str, scope: List[str], redirect_uri: str, state: str
    ):
        # https://docs.aws.amazon.com/cognito/latest/developerguide/authorization-endpoint.html
        auth_url = cls.oidc_configuration_document.authorization_endpoint
        params = {
            "state": state,
            "client_id": client_id,
            "response_type": response_type,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scope),
        }

        logger.debug("Building final URL...")
        url_parse = parse.urlparse(auth_url)
        query = url_parse.query
        url_dict = dict(parse.parse_qsl(query))
        url_dict.update(params)
        url_new_query = parse.urlencode(url_dict)
        url_parse = url_parse._replace(query=url_new_query)
        final_url = parse.urlunparse(url_parse)

        logger.debug("URL which has been built: %s", final_url)
        return final_url

    @classmethod
    def acquire_token_by_auth_code_flow(
        cls, client_id: str, client_secret: str, code: str, scope: List[str], redirect_uri: str
    ) -> Tuple[TokensBoundToSomeUser, Claims]:
        # https://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html
        token_endpoint = cls.oidc_configuration_document.token_endpoint
        app_credentials = f"{client_id}:{client_secret}"
        app_credentials_encoded = b64encode(app_credentials.encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {app_credentials_encoded}",
        }
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scope),
        }
        response = requests.post(token_endpoint, headers=headers, data=body)
        content: TokensBoundToSomeUser = response.json()
        claims = cls.retrieve_claims_otherwise_raise_exception_if_token_is_invalid(content["id_token"])
        return content, claims

    @classmethod
    def get_user_info(cls, access_token) -> dict:
        # https://docs.aws.amazon.com/cognito/latest/developerguide/userinfo-endpoint.html
        userinfo_endpoint = cls.oidc_configuration_document.userinfo_endpoint
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        result = requests.get(userinfo_endpoint, headers=headers)
        # Sample result
        # {
        #     "sub": "bbf338b6-fa67-4b91-baaf-24886a31b3d6",
        #     "email_verified": "true",
        #     "email": "willianlimaantunes@gmail.com",
        #     "username": "willian",
        # }
        body = result.json()

        return body
