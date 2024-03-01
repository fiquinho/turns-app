from dataclasses import dataclass
from functools import partial

from turns_app.defaults import TESTS_PATH
from turns_app.utils.dataclass_utils import BaseDataclass
from turns_app.utils.dotenv_utils import config_from_env


TEST_ENV_FILE = TESTS_PATH / "test_utils" / ".env.test"


@dataclass
class TestConfig(BaseDataclass):
    USER: str
    ID: int
    ADMIN: bool
    PROD: bool


def test_config_from_env():

    config: TestConfig = config_from_env(TEST_ENV_FILE, TestConfig)

    assert config.USER == "test_user"
    assert config.ID == 123
    assert config.ADMIN is True
    assert config.PROD is False
