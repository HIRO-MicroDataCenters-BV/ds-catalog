# coding: utf-8

"""
    Data Space Catalog

    The service provides a REST API for managing and sharing catalog data. Interacts with connector services to obtain information about data products.

    The version of the OpenAPI document: 0.1.1
    Contact: all-hiro@hiro-microdatacenters.nl
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List
from ds_catalog.models.distribution import Distribution
from typing import Optional, Set
from typing_extensions import Self

class DatasetImportForm(BaseModel):
    """
    DatasetImportForm
    """ # noqa: E501
    identifier: StrictStr
    title: StrictStr
    theme: List[StrictStr]
    distribution: List[Distribution]
    __properties: ClassVar[List[str]] = ["identifier", "title", "theme", "distribution"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of DatasetImportForm from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in distribution (list)
        _items = []
        if self.distribution:
            for _item_distribution in self.distribution:
                if _item_distribution:
                    _items.append(_item_distribution.to_dict())
            _dict['distribution'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of DatasetImportForm from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "identifier": obj.get("identifier"),
            "title": obj.get("title"),
            "theme": obj.get("theme"),
            "distribution": [Distribution.from_dict(_item) for _item in obj["distribution"]] if obj.get("distribution") is not None else None
        })
        return _obj


