from typing import TypeVar

from pydantic import BaseModel

from src.database import Base

SchemaType = TypeVar("SchemaType", bound=BaseModel)
DBModelType = TypeVar("DBModelType", bound=Base)


class DataMapper:
    db_model: type[DBModelType] = None
    schema: type[SchemaType] = None

    @classmethod
    def map_to_domain_entity(cls, db_model):
        return cls.schema.model_validate(db_model, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, schema):
        return cls.db_model(**schema.model_dump())

    @classmethod
    def map_to_persistence_entity_with_unset_filter(
        cls, data, exclude_unset: bool = False
    ):
        return cls.db_model(**data.model_dump(exclude_unset=exclude_unset))
