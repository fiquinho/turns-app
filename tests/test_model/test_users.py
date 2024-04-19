import json

import pytest

from tests.defaults import TEST_USERS_FILE
from turns_app.model.users import User, MongoUsersManager, UserExistsError, NamedUser
from tests.conftest import test_config


@pytest.fixture
def named_user_dict() -> dict[str, str]:
    return {
        "id": "USER_01",
        "name": "John Doe"
    }


@pytest.fixture
def user_dict() -> dict[str, str]:
    return {
        "id": "USER_03",
        "name": "Mario Bros",
        "email": "mario@nintendo.com",
        "phone": "9995551489",
        "activity": "Plomero"
    }


@pytest.fixture
def named_user(named_user_dict) -> NamedUser:
    return NamedUser.from_dict(named_user_dict)


@pytest.fixture
def user(user_dict) -> User:
    return User.from_dict(user_dict)


@pytest.fixture
def users_list() -> list[User]:
    with open(TEST_USERS_FILE, 'r', encoding="utf8") as file:
        users = json.load(file)
    return [User.from_dict(_user) for _user in users]


def test_named_user_creation(named_user_dict):
    named_user = NamedUser.from_dict(named_user_dict)
    assert named_user.id == "USER_01"
    assert named_user.name == "John Doe"


def test_user_creation(user_dict):
    user = User.from_dict(user_dict)
    assert user.id == "USER_03"
    assert user.name == "Mario Bros"
    assert user.email == "mario@nintendo.com"
    assert user.phone == "9995551489"
    assert user.activity == "Plomero"


def test_named_user_to_dict(named_user_dict):
    named_user = NamedUser.from_dict(named_user_dict)
    result = named_user.to_dict()
    assert result == named_user_dict


def test_user_to_dict(user_dict):
    user = User.from_dict(user_dict)
    result = user.to_dict()
    assert result == user_dict


def test_user_to_named_user(user_dict):
    user = User.from_dict(user_dict)
    named_user = user.get_named_user()
    assert named_user.id == user.id
    assert named_user.name == user.name


def test_users_manager_create(test_config, user):
    manger = MongoUsersManager(test_config.mongo)
    manger.create_user(user)

    with pytest.raises(UserExistsError):
        manger.create_user(user)


def test_users_manager_get_by_id(test_config, users_list):
    manger = MongoUsersManager(test_config.mongo)

    result = manger.get_by_id(users_list[0].id)
    assert result == users_list[0]

    result = manger.get_by_id("USER_05")
    assert result is None
