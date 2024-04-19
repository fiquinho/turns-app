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

        hints = get_type_hints(cls)
        constructor_args = {key: value for key, value in values.items()
                            if key in hints}

        init_args = {}
        for key, value in constructor_args.items():
            attr_type = hints[key]
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
        Also converts nested dataclasses to dictionaries.

        :return: A dictionary representation of the dataclass
        """

        hints = get_type_hints(self.__class__)
        result = {}
        for key, attr_type in hints.items():
            value = getattr(self, key)
            if issubclass(attr_type, BaseDataclass):
                result[key] = value.to_dict()
            else:
                result[key] = value

        return result


BaseDataclassInstance = TypeVar('BaseDataclassInstance', bound=BaseDataclass)
