from typing import List, Type

import attrs


def snake_to_pascal_case(string: str) -> str:
    """Convert a snake_case string to PascalCase."""
    return "".join(word.title() for word in string.split("_"))


def ds_names(
    cls: Type,  # noqa: ARG001
    fields: List[attrs.Attribute],
) -> List[attrs.Attribute]:
    """Return field aliases."""
    return [field.evolve(alias=snake_to_pascal_case(field.name)) for field in fields]
