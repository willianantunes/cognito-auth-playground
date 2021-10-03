from dataclasses import asdict
from unittest import TestCase

import pytest

from cognito_custom_ui_and_api import settings
from cognito_custom_ui_and_api.apps.core.services.cognito_user_pool import CognitoUserPool
from cognito_custom_ui_and_api.apps.core.services.cognito_user_pool import UserToBeRegistered
from cognito_custom_ui_and_api.apps.core.services.exceps import UsernameExistsException


class BaseTestCase(TestCase):
    cognito_user_pool: CognitoUserPool

    @classmethod
    def setUpClass(cls) -> None:
        cls.cognito_user_pool = CognitoUserPool()

    # @classmethod
    # def tearDownClass(cls) -> None:
    #     users, _ = cls.cognito_user_pool.list_users()
    #     for user in users:
    #         cls.cognito_user_pool.delete_user(user.username)


class UserActionsTest(BaseTestCase):
    def test_should_create_user(self):
        # Arrange
        user = UserToBeRegistered("jafar@agrabah.com", "Sorcerer Jafar", "you-are-late")
        # Act
        self.cognito_user_pool.create_user(user)
        # Assert
        user = self.cognito_user_pool.retrieve_user(user.email)
        assert user.enabled
        assert user.status == "UNCONFIRMED"
        assert user.attributes["sub"]
        del user.attributes["sub"]
        assert user.attributes == {"email_verified": "false", "name": "Sorcerer Jafar", "email": "jafar@agrabah.com"}

    def test_should_raise_exception_if_username_already_exists(self):
        # Arrange
        user = UserToBeRegistered("jasmine@agrabah.com", "Princess Jasmine", "the-law-is-wrong")
        # Act and assert
        with pytest.raises(UsernameExistsException):
            self.cognito_user_pool.create_user(user)
            self.cognito_user_pool.create_user(user)


class AdminActionsTest(BaseTestCase):
    def test_should_return_nothing_as_no_user_can_be_retrieved(self):
        # Arrange
        username = "aladdin@agrabah.com"
        # Act
        user = self.cognito_user_pool.retrieve_user(username)
        # Assert
        assert not user

    def test_should_return_details_about_user_pool_client(self):
        # Arrange
        client_id = settings.AWS_COGNITO_APP_CLIENT_ID
        # Act
        app_client = self.cognito_user_pool.retrieve_user_pool_client(client_id)
        app_client_fake = self.cognito_user_pool.retrieve_user_pool_client("fake_client_id")
        # Assert
        assert not app_client_fake
        assert app_client.id
        assert app_client.created_at
        assert app_client.updated_at
        assert app_client.secret
        app_client_as_dict = asdict(app_client)
        del app_client_as_dict["created_at"]
        del app_client_as_dict["updated_at"]
        del app_client_as_dict["secret"]
        del app_client_as_dict["id"]
        assert app_client_as_dict == {
            "name": "poc-djangoclient-appclientcognito-tmp",
            "refresh_token_validity": 30,
            "read_attributes": ["email", "email_verified", "name", "preferred_username"],
            "supported_identity_providers": ["COGNITO"],
            "callback_urls": ["http://localhost:8000/api/v1/response-oidc"],
            "logout_urls": ["http://localhost:8000/logout"],
            "allowed_oauth_flows": ["code"],
            "allowed_oauth_scopes": ["email", "openid", "profile"],
            "allowed_oauth_flows_user_pool_client": True,
            "enable_token_revocation": True,
        }


class AuthorizationCodeTest(BaseTestCase):
    def test_should_mimic_authorization_code_flow(self):
        grant_type = "code"
        username, password = "jafar@agrabah.com", "you-are-late"
        result = self.cognito_user_pool.authenticate(username, password, grant_type)
        assert result
