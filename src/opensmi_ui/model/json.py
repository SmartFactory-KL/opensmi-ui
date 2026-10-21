from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


# basic error class for non-enabled stuff
class ModuleDisabledError(RuntimeError):
    """Raised whenever a module is simply not enabled but functionality was still used"""


# base class for all json based models. converts snake_case_style to camelCaseStyle for JSON in both directions
class JsonInModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
        ),
        populate_by_name=True,
    )


class JsonBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )


class JsonOutModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        ),
    )
