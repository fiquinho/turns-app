import inspect
from dataclasses import dataclass
from typing import Any, get_type_hints, TypeVar, get_args


@dataclass
class BaseDataclass:

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> 'BaseDataclass':
        """
        Construct a dataclass from a dictionary of values.
        Allows extra values to be passed in, but will ignore them.
        Also allows nested dataclasses to be constructed.

        :param values: The dictionary of values to use to construct the dataclass
        :return: A new instance of the dataclass
        """

        attributes = inspect.signature(cls).parameters
        constructor_args = {key: value for key, value in values.items()
                            if key in attributes}

        init_args = {}
        for (key, value), attr_type in zip(constructor_args.items(), get_type_hints(cls).values()):
            if issubclass(attr_type, BaseDataclass):
                init_args[key] = attr_type.from_dict(value)
            else:
                init_args[key] = value

        # noinspection PyArgumentList
        return cls(**init_args)

    def __post_init__(self):
        """Ensure that the dataclass has been constructed with the correct types.
        Raises a TypeError if at least one type is incorrect."""

        hints = get_type_hints(self)
        for attr, attr_type in hints.items():
            value = getattr(self, attr)
            if hasattr(attr_type, "__origin__") and attr_type.__origin__ == list:
                # If the attribute type is a list, get its inner type
                inner_type = get_args(attr_type)[0]
                if not all(isinstance(item, inner_type) for item in value):
                    raise TypeError(f"Attribute '{attr}' must be a list of type '{inner_type}', got '{type(value)}'")
            elif not isinstance(value, attr_type):
                raise TypeError(f"Attribute '{attr}' must be of type '{attr_type}', got '{type(value)}'")

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the dataclass to a dictionary.

        :return: A dictionary representation of the dataclass
        """
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}


BaseDataclassInstance = TypeVar('BaseDataclassInstance', bound=BaseDataclass)
