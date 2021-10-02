from unittest import TestCase

import pytest

from cognito_custom_ui_and_api.apps.core.services.cognito_user_pool import CognitoUserPool
from cognito_custom_ui_and_api.apps.core.services.cognito_user_pool import UserToBeRegistered
from cognito_custom_ui_and_api.apps.core.services.exceps import UsernameExistsException


class BaseTestCase(TestCase):
    cognito_user_pool: CognitoUserPool

    @classmethod
    def setUpClass(cls) -> None:
        cls.cognito_user_pool = CognitoUserPool()

    @classmethod
    def tearDownClass(cls) -> None:
        users, _ = cls.cognito_user_pool.list_users()
        for user in users:
            cls.cognito_user_pool.delete_user(user.username)


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


class AuthorizationCodeTest(BaseTestCase):
    pass
