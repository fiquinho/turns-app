import inspect
from dataclasses import dataclass
from typing import Any, get_type_hints, TypeVar


@dataclass
class BaseDataclass:

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> 'BaseDataclass':
        """
        Construct a dataclass from a dictionary of values.
        Allows extra values to be passed in, but will ignore them.

        :param values: The dictionary of values to use to construct the dataclass
        :return: A new instance of the dataclass
        """

        attributes = inspect.signature(cls).parameters
        constructor_args = {key: value for key, value in values.items()
                            if key in attributes}

        # noinspection PyArgumentList
        return cls(**constructor_args)

    def __post_init__(self):
        """Ensure that the dataclass has been constructed with the correct types.
        Raises a TypeError if at least one type is incorrect."""

        hints = get_type_hints(self)
        for attr, attr_type in hints.items():
            value = getattr(self, attr)
            if not isinstance(value, attr_type):
                raise TypeError(f"Attribute '{attr}' must be of type '{attr_type}', got '{type(value)}'")


BaseDataclassInstance = TypeVar('BaseDataclassInstance', bound=BaseDataclass)
