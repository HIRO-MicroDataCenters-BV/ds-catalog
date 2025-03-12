from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict as PydanticConfigDict
from pydantic.alias_generators import to_camel


class BaseModel(PydanticBaseModel):
    model_config = PydanticConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
