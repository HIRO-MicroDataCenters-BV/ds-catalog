from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from ..entities import (
    Catalog,
    CatalogImport,
    Checksum,
    DataService,
    Dataset,
    DatasetImport,
    DatasetInput,
    Distribution,
    NewDataset,
    Person,
)


class PersonFactory(ModelFactory[Person]):
    __model__ = Person


class CatalogFactory(ModelFactory[Catalog]):
    __model__ = Catalog


class CatalogImportFactory(ModelFactory[CatalogImport]):
    __model__ = CatalogImport


class ChecksumFactory(ModelFactory[Checksum]):
    __model__ = Checksum


class DataServiceFactory(ModelFactory[DataService]):
    __model__ = DataService


class DistributionFactory(ModelFactory[Distribution]):
    __model__ = Distribution

    checksum = ChecksumFactory
    access_service = Use(DataServiceFactory.batch, size=1)


class NewDatasetFactory(ModelFactory[NewDataset]):
    __model__ = NewDataset

    catalog = CatalogFactory
    creator = PersonFactory
    distribution = Use(DistributionFactory.batch, size=1)


class DatasetFactory(ModelFactory[Dataset]):
    __model__ = Dataset

    catalog = CatalogFactory
    creator = PersonFactory
    distribution = Use(DistributionFactory.batch, size=1)


class DatasetInputFactory(ModelFactory[DatasetInput]):
    __model__ = DatasetInput

    distribution = Use(DistributionFactory.batch, size=1)


class DatasetImportFactory(ModelFactory[DatasetImport]):
    __model__ = DatasetImport

    catalog = CatalogImportFactory
    distribution = Use(DistributionFactory.batch, size=1)
