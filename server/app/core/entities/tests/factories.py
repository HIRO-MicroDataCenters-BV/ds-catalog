from polyfactory import Use
from polyfactory.factories import DataclassFactory

from ..catalog import DataService, Dataset, DatasetImport, DatasetInput, Distribution
from ..person import Person


class PersonFactory(DataclassFactory[Person]):
    __model__ = Person


class DataServiceFactory(DataclassFactory[DataService]):
    __model__ = DataService


class DistributionFactory(DataclassFactory[Distribution]):
    __model__ = Distribution

    access_service = Use(DataServiceFactory.batch, size=1)


class DatasetFactory(DataclassFactory[Dataset]):
    __model__ = Dataset

    creator = PersonFactory
    distribution = Use(DistributionFactory.batch, size=1)


class DatasetInputFactory(DataclassFactory[DatasetInput]):
    __model__ = DatasetInput

    distribution = Use(DistributionFactory.batch, size=1)


class DatasetImportFactory(DataclassFactory[DatasetImport]):
    __model__ = DatasetImport

    distribution = Use(DistributionFactory.batch, size=1)
