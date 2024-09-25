from datetime import datetime

import pytz
from neomodel import (
    ArrayProperty,
    AsyncOne,
    AsyncOneOrMore,
    AsyncRelationshipFrom,
    AsyncRelationshipTo,
    AsyncStructuredNode,
    AsyncStructuredRel,
    AsyncZeroOrMore,
    BooleanProperty,
    DateProperty,
    IntegerProperty,
    StringProperty,
    UniqueIdProperty,
)


class PersonNode(AsyncStructuredNode):
    __label__ = "Person"

    identifier = UniqueIdProperty()
    name = StringProperty(required=True, index=True)


class ChecksumNode(AsyncStructuredNode):
    __label__ = "Checksum"

    algorithm = StringProperty(required=True)
    checksum_value = StringProperty(required=True)


class CatalogNode(AsyncStructuredNode):
    __label__ = "Catalog"

    identifier = StringProperty(unique_index=True, required=True)
    creator = AsyncRelationshipTo(
        PersonNode,
        "CREATOR",
        model=AsyncStructuredRel,
        cardinality=AsyncOne,
    )
    dataset = AsyncRelationshipTo(
        "DatasetNode",
        "DATASET",
        model=AsyncStructuredRel,
        cardinality=AsyncZeroOrMore,
    )
    service = AsyncRelationshipTo(
        "DataServiceNode",
        "SERVICE",
        model=AsyncStructuredRel,
        cardinality=AsyncZeroOrMore,
    )


class DatasetNode(AsyncStructuredNode):
    __label__ = "Dataset"

    identifier = UniqueIdProperty()
    title = StringProperty(required=True, index=True)
    description = StringProperty(required=True)
    keyword = ArrayProperty(StringProperty(), required=True)
    license = StringProperty(required=True)
    issued = DateProperty(index=True, default=lambda: datetime.now(pytz.utc).date())
    theme = ArrayProperty(StringProperty(), required=True, index=True)
    is_local = BooleanProperty(index=True)
    is_shared = BooleanProperty(index=True)
    creator = AsyncRelationshipTo(
        PersonNode,
        "CREATOR",
        model=AsyncStructuredRel,
        cardinality=AsyncOne,
    )
    distribution = AsyncRelationshipTo(
        "DistributionNode",
        "DISTRIBUTION",
        model=AsyncStructuredRel,
        cardinality=AsyncOneOrMore,
    )

    services = AsyncRelationshipFrom(
        "DataServiceNode",
        "SERVES_DATASET",
        model=AsyncStructuredRel,
        cardinality=AsyncOneOrMore,
    )
    catalog = AsyncRelationshipFrom(CatalogNode, "DATASET", cardinality=AsyncOne)


class DistributionNode(AsyncStructuredNode):
    __label__ = "Distribution"

    byte_size = IntegerProperty(index=True, required=False)
    media_type = StringProperty(required=True, index=True)
    checksum = AsyncRelationshipTo(
        "ChecksumNode",
        "CHECKSUM",
        model=AsyncStructuredRel,
        cardinality=AsyncOne,
    )
    access_service = AsyncRelationshipTo(
        "DataServiceNode",
        "ACCESS_SERVICE",
        model=AsyncStructuredRel,
        cardinality=AsyncOneOrMore,
    )


class DataServiceNode(AsyncStructuredNode):
    __label__ = "DataService"

    endpoint_url = StringProperty(required=True)
    serves_dataset = AsyncRelationshipTo(
        DatasetNode,
        "SERVES_DATASET",
        model=AsyncStructuredRel,
        cardinality=AsyncOne,
    )
