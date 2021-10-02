import base64
import hashlib
import hmac
import logging

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import Union

import boto3
import botocore

from mypy_boto3_cognito_idp.type_defs import GetUserResponseTypeDef

from cognito_custom_ui_and_api import settings
from cognito_custom_ui_and_api.apps.core.services.exceps import UsernameExistsException

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UserToBeRegistered:
    email: str
    name: str
    password: str


@dataclass(frozen=True)
class UserDetails:
    username: str
    attributes: Dict[str, Union[str, int]]
    created_at: datetime
    updated_at: datetime
    enabled: bool
    status: str


GrantType = Literal["ropc", "code"]


class CognitoUserPool:
    def __init__(self):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/index.html#sdk-features
        self.client = boto3.client(
            "cognito-idp",
            region_name=settings.AWS_COGNITO_REGION,
            aws_access_key_id=settings.AWS_COGNITO_SERVICE_ACCOUNT_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_COGNITO_SERVICE_ACCOUNT_ACCESS_SECRET,
        )
        self.app_client_id = settings.AWS_COGNITO_APP_CLIENT_ID
        self.app_client_secret = settings.AWS_COGNITO_APP_CLIENT_SECRET
        self.user_pool_id = settings.AWS_COGNITO_USER_POOL_ID

    def create_user(self, user: UserToBeRegistered) -> None:
        # https://vemel.github.io/boto3_stubs_docs/mypy_boto3_cognito_idp/client.html#sign_up
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html#CognitoIdentityProvider.Client.sign_up
        logger.debug("Creating user with name %s", user.name)
        user_attributes = [
            {
                "Name": "name",
                "Value": user.name,
            },
            {
                "Name": "email",
                "Value": user.email,
            },
        ]
        secret_hash = self._generete_secret_hash(user.email)
        try:
            sign_up_response_as_json = self.client.sign_up(
                ClientId=self.app_client_id,
                Username=user.email,
                Password=user.password,
                UserAttributes=user_attributes,
                SecretHash=secret_hash,
            )
            logger.debug("Sign up response: %s", sign_up_response_as_json)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "UsernameExistsException":
                raise UsernameExistsException
            else:
                raise NotImplementedError

    def retrieve_user_through_access_token(self, access_token: str) -> GetUserResponseTypeDef:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html#CognitoIdentityProvider.Client.get_user
        return self.client.get_user(AccessToken=access_token)

    def retrieve_user(self, username: str) -> Optional[UserDetails]:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html#CognitoIdentityProvider.Client.admin_get_user
        try:
            response_as_json = self.client.admin_get_user(UserPoolId=self.user_pool_id, Username=username)
            return self._create_user_details(response_as_json)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] != "UserNotFoundException":
                raise NotImplementedError
        return None

    def delete_user(self, username: str):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html#CognitoIdentityProvider.Client.admin_delete_user
        self.client.admin_delete_user(UserPoolId=self.user_pool_id, Username=username)

    def list_users(self, pagination_token: str = None, limit=50) -> Tuple[List[UserDetails], Optional[str]]:
        users = []
        params = {"UserPoolId": self.user_pool_id, "Limit": limit}

        if not pagination_token:
            logger.debug("Listing users without pagination token")
            response_as_json = self.client.list_users(**params)
        else:
            logger.debug("Listing users with pagination token")
            params["PaginationToken"] = pagination_token
            response_as_json = self.client.list_users(**params)

        for user in response_as_json["Users"]:
            built_user = self._create_user_details(user)
            users.append(built_user)

        return users, response_as_json.get("PaginationToken")

    def authenticate(self, username: str, password: str, grant_type: GrantType = "ropc"):
        if grant_type == "ropc":
            auth_parameters = {"USERNAME": username, "PASSWORD": password}
            response_as_json = self.client.initiate_auth(
                ClientId=self.app_client_id, AuthFlow="USER_PASSWORD_AUTH", AuthParameters=auth_parameters
            )
        elif grant_type == "code":
            pass
        else:
            raise NotImplementedError
        raise NotImplementedError

    def _generete_secret_hash(self, username: str) -> str:
        # https://aws.amazon.com/premiumsupport/knowledge-center/cognito-unable-to-verify-secret-hash/
        message = bytes(username + self.app_client_id, "utf-8")
        key = bytes(self.app_client_secret, "utf-8")
        return base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()

    def _create_user_details(self, user_from_cognito: dict):
        username = user_from_cognito["Username"]
        created_at = user_from_cognito["UserCreateDate"]
        updated_at = user_from_cognito["UserLastModifiedDate"]
        enabled = user_from_cognito["Enabled"]
        status = user_from_cognito["UserStatus"]
        attributes = {}
        users_attributes = user_from_cognito.get("UserAttributes")
        users_attributes = users_attributes if users_attributes else user_from_cognito["Attributes"]
        for attribute in users_attributes:
            key, value = attribute["Name"], attribute["Value"]
            attributes[key] = value
        return UserDetails(username, attributes, created_at, updated_at, enabled, status)
