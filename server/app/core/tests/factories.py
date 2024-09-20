from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from ..entities import (
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

    creator = PersonFactory
    distribution = Use(DistributionFactory.batch, size=1)


class DatasetFactory(ModelFactory[Dataset]):
    __model__ = Dataset

    creator = PersonFactory
    distribution = Use(DistributionFactory.batch, size=1)


class DatasetInputFactory(ModelFactory[DatasetInput]):
    __model__ = DatasetInput

    distribution = Use(DistributionFactory.batch, size=1)


class DatasetImportFactory(ModelFactory[DatasetImport]):
    __model__ = DatasetImport

    distribution = Use(DistributionFactory.batch, size=1)
