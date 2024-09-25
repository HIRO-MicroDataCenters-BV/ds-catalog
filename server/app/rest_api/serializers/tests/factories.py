from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from ..catalog import (
    Catalog,
    CatalogImportForm,
    Checksum,
    DataService,
    Dataset,
    DatasetForm,
    DatasetImportForm,
    DatasetShareForm,
    Distribution,
)
from ..person import Person


class PersonFactory(ModelFactory[Person]):
    __model__ = Person


class CatalogFactory(ModelFactory[Catalog]):
    __model__ = Catalog


class CatalogImportFormFactory(ModelFactory[CatalogImportForm]):
    __model__ = CatalogImportForm


class ChecksumFactory(ModelFactory[Checksum]):
    __model__ = Checksum


class DataServiceFactory(ModelFactory[DataService]):
    __model__ = DataService


class DistributionFactory(ModelFactory[Distribution]):
    __model__ = Distribution

    checksum = ChecksumFactory
    access_service = Use(DataServiceFactory.batch, size=1)


class DatasetFactory(ModelFactory[Dataset]):
    __model__ = Dataset

    catalog = CatalogFactory
    creator = PersonFactory
    distribution = Use(DistributionFactory.batch, size=1)


class DatasetFormFactory(ModelFactory[DatasetForm]):
    __model__ = DatasetForm

    distribution = Use(DistributionFactory.batch, size=1)


class DatasetShareFormFactory(ModelFactory[DatasetShareForm]):
    __model__ = DatasetShareForm


class DatasetImportFormFactory(ModelFactory[DatasetImportForm]):
    __model__ = DatasetImportForm

    catalog = CatalogImportFormFactory
    distribution = Use(DistributionFactory.batch, size=1)
