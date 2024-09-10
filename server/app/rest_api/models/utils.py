from typing import Any, ClassVar, Protocol

import dataclasses

from .base import BaseModel


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]


def entity_to_dict(
    entity: DataclassInstance, exclude_fields: set[str] | None = None
) -> dict[str, Any]:
    result = dataclasses.asdict(entity)
    if exclude_fields is not None:
        for field_name in exclude_fields:
            del result[field_name]
    return result


def model_to_dict(
    model: BaseModel, exclude_fields: set[str] | None = None
) -> dict[str, Any]:
    return model.model_dump(exclude=exclude_fields)
