import pytest
from dataclasses import dataclass


from turns_app.utils.dataclass_utils import BaseDataclass


@dataclass
class ExampleDataclass(BaseDataclass):
    idx: int
    name: str
    optional: str = 'default'


@pytest.fixture
def example_dict():
    return {'idx': 1, 'name': 'name', 'optional': 'optional'}


@pytest.fixture
def example_dict_missing_optional():
    return {'idx': 1, 'name': 'name'}


@pytest.fixture
def example_dict_extra_key():
    return {'idx': 1, 'name': 'name', 'optional': 'optional', 'extra': 'extra'}


@pytest.fixture
def example_dict_missing_optional_extra():
    return {'idx': 1, 'name': 'name', 'extra': 'extra'}


@pytest.fixture
def example_dict_missing_required():
    return {'name': 'name', 'optional': 'optional'}


@pytest.fixture
def wrong_type_dict():
    return {'idx': '1', 'name': 'name', 'optional': 'optional'}


def test_post_init(wrong_type_dict):
    with pytest.raises(TypeError):
        ExampleDataclass.from_dict(wrong_type_dict)


def test_from_dict(example_dict, example_dict_missing_optional, example_dict_extra_key,
                   example_dict_missing_optional_extra, example_dict_missing_required):
    result = ExampleDataclass.from_dict(example_dict)
    assert result.idx == 1
    assert result.name == 'name'
    assert result.optional == 'optional'

    result = ExampleDataclass.from_dict(example_dict_missing_optional)
    assert result.idx == 1
    assert result.name == 'name'
    assert result.optional == 'default'

    result = ExampleDataclass.from_dict(example_dict_extra_key)
    assert result.idx == 1
    assert result.name == 'name'
    assert result.optional == 'optional'

    result = ExampleDataclass.from_dict(example_dict_missing_optional_extra)
    assert result.idx == 1
    assert result.name == 'name'
    assert result.optional == 'default'

    with pytest.raises(TypeError):
        ExampleDataclass.from_dict(example_dict_missing_required)
