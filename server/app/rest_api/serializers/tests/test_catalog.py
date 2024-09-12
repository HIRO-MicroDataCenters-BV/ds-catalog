from app.core.entities.tests import factories as entities_factories

from ..catalog import DataService, Dataset, DatasetForm, DatasetImportForm, Distribution
from ..person import Person
from .factories import (
    DataServiceFactory,
    DatasetFactory,
    DatasetFormFactory,
    DatasetImportFormFactory,
    DistributionFactory,
)


class TestDataService:
    def test_to_entity(self):
        data_service = DataServiceFactory.build()
        entity = data_service.to_entity()

        assert entity.endpoint_url == data_service.endpoint_url

    def test_from_entity(self):
        entity = entities_factories.DataServiceFactory.build()
        data_service = DataService.from_entity(entity)

        assert entity.endpoint_url == data_service.endpoint_url


class TestDistribution:
    def test_to_entity(self):
        distribution = DistributionFactory.build()
        entity = distribution.to_entity()

        assert entity.bytesize == distribution.bytesize
        assert entity.mimetype == distribution.mimetype
        assert entity.checksum == distribution.checksum
        assert entity.access_service == [
            i.to_entity() for i in distribution.access_service
        ]

    def test_from_entity(self):
        entity = entities_factories.DistributionFactory.build()
        distribution = Distribution.from_entity(entity)

        assert distribution.bytesize == entity.bytesize
        assert distribution.mimetype == entity.mimetype
        assert distribution.checksum == entity.checksum
        assert distribution.access_service == [
            DataService.from_entity(i) for i in entity.access_service
        ]


class TestDataset:
    def test_to_entity(self):
        dataset = DatasetFactory.build()
        entity = dataset.to_entity()

        assert entity.identifier == dataset.identifier
        assert entity.title == dataset.title
        assert entity.is_local == dataset.is_local
        assert entity.is_shared == dataset.is_shared
        assert entity.issued == dataset.issued
        assert entity.theme == dataset.theme
        assert entity.creator == dataset.creator.to_entity()
        assert entity.distribution == [i.to_entity() for i in dataset.distribution]

    def test_from_entity(self):
        entity = entities_factories.DatasetFactory.build()
        dataset = Dataset.from_entity(entity)

        assert dataset.identifier == entity.identifier
        assert dataset.title == entity.title
        assert dataset.is_local == entity.is_local
        assert dataset.is_shared == entity.is_shared
        assert dataset.issued == entity.issued
        assert dataset.theme == entity.theme
        assert dataset.creator == Person.from_entity(entity.creator)
        assert dataset.distribution == [
            Distribution.from_entity(i) for i in entity.distribution
        ]


class TestDatasetForm:
    def test_to_entity(self):
        dataset_form = DatasetFormFactory.build()
        entity = dataset_form.to_entity()

        assert entity.title == dataset_form.title
        assert entity.theme == dataset_form.theme
        assert entity.distribution == [i.to_entity() for i in dataset_form.distribution]

    def test_from_entity(self):
        entity = entities_factories.DatasetInputFactory.build()
        dataset_form = DatasetForm.from_entity(entity)

        assert dataset_form.title == entity.title
        assert dataset_form.theme == entity.theme
        assert dataset_form.distribution == [
            Distribution.from_entity(i) for i in entity.distribution
        ]


class TestDatasetImportForm:
    def test_to_entity(self):
        import_form = DatasetImportFormFactory.build()
        entity = import_form.to_entity()

        assert entity.identifier == import_form.identifier
        assert entity.title == import_form.title
        assert entity.theme == import_form.theme
        assert entity.distribution == [i.to_entity() for i in import_form.distribution]

    def test_from_entity(self):
        entity = entities_factories.DatasetImportFactory.build()
        import_form = DatasetImportForm.from_entity(entity)

        assert import_form.identifier == entity.identifier
        assert import_form.title == entity.title
        assert import_form.theme == entity.theme
        assert import_form.distribution == [
            Distribution.from_entity(i) for i in entity.distribution
        ]
