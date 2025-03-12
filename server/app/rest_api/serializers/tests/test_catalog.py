from app.core.tests import factories as entities_factories

from ..catalog import (
    Catalog,
    CatalogImportForm,
    Checksum,
    DataService,
    Dataset,
    DatasetForm,
    DatasetImportForm,
    Distribution,
)
from ..person import Person
from .factories import (
    CatalogFactory,
    CatalogImportFormFactory,
    DataServiceFactory,
    DatasetFactory,
    DatasetFormFactory,
    DatasetImportFormFactory,
    DistributionFactory,
)


class TestCatalog:
    def test_to_entity(self) -> None:
        catalog = CatalogFactory.build()
        entity = catalog.to_entity()

        assert entity.identifier == catalog.identifier
        assert entity.title == catalog.title
        assert entity.description == catalog.description

    def test_from_entity(self) -> None:
        entity = entities_factories.CatalogFactory.build()
        catalog = Catalog.from_entity(entity)

        assert entity.identifier == catalog.identifier
        assert entity.title == catalog.title
        assert entity.description == catalog.description


class TestCatalogImportForm:
    def test_to_entity(self) -> None:
        catalog_import_form = CatalogImportFormFactory.build()
        entity = catalog_import_form.to_entity()

        assert entity.title == catalog_import_form.title
        assert entity.description == catalog_import_form.description

    def test_from_entity(self) -> None:
        entity = entities_factories.CatalogImportFactory.build()
        catalog_import_form = CatalogImportForm.from_entity(entity)

        assert entity.title == catalog_import_form.title
        assert entity.description == catalog_import_form.description


class TestDataService:
    def test_to_entity(self) -> None:
        data_service = DataServiceFactory.build()
        entity = data_service.to_entity()

        assert entity.endpoint_url == data_service.endpoint_url

    def test_from_entity(self) -> None:
        entity = entities_factories.DataServiceFactory.build()
        data_service = DataService.from_entity(entity)

        assert entity.endpoint_url == data_service.endpoint_url


class TestDistribution:
    def test_to_entity(self) -> None:
        distribution = DistributionFactory.build()
        entity = distribution.to_entity()

        assert entity.byte_size == distribution.byte_size
        assert entity.media_type == distribution.media_type
        assert entity.checksum == distribution.checksum.to_entity()
        assert entity.access_service == [
            i.to_entity() for i in distribution.access_service
        ]

    def test_from_entity(self) -> None:
        entity = entities_factories.DistributionFactory.build()
        distribution = Distribution.from_entity(entity)

        assert distribution.byte_size == entity.byte_size
        assert distribution.media_type == entity.media_type
        assert distribution.checksum == Checksum.from_entity(entity.checksum)
        assert distribution.access_service == [
            DataService.from_entity(i) for i in entity.access_service
        ]


class TestDataset:
    def test_to_entity(self) -> None:
        dataset = DatasetFactory.build()
        entity = dataset.to_entity()

        assert entity.identifier == dataset.identifier
        assert entity.title == dataset.title
        assert entity.description == dataset.description
        assert entity.keyword == dataset.keyword
        assert entity.license == dataset.license
        assert entity.is_local == dataset.is_local
        assert entity.is_shared == dataset.is_shared
        assert entity.issued == dataset.issued
        assert entity.theme == dataset.theme
        assert entity.catalog == dataset.catalog.to_entity()
        assert entity.creator == dataset.creator.to_entity()
        assert entity.distribution == [i.to_entity() for i in dataset.distribution]

    def test_from_entity(self) -> None:
        entity = entities_factories.DatasetFactory.build()
        dataset = Dataset.from_entity(entity)

        assert dataset.identifier == entity.identifier
        assert dataset.title == entity.title
        assert entity.description == dataset.description
        assert entity.keyword == dataset.keyword
        assert entity.license == dataset.license
        assert dataset.is_local == entity.is_local
        assert dataset.is_shared == entity.is_shared
        assert dataset.issued == entity.issued
        assert dataset.theme == entity.theme
        assert dataset.catalog == Catalog.from_entity(entity.catalog)
        assert dataset.creator == Person.from_entity(entity.creator)
        assert dataset.distribution == [
            Distribution.from_entity(i) for i in entity.distribution
        ]


class TestDatasetForm:
    def test_to_entity(self) -> None:
        dataset_form = DatasetFormFactory.build()
        entity = dataset_form.to_entity()

        assert entity.title == dataset_form.title
        assert entity.description == dataset_form.description
        assert entity.keyword == dataset_form.keyword
        assert entity.license == dataset_form.license
        assert entity.theme == dataset_form.theme
        assert entity.distribution == [i.to_entity() for i in dataset_form.distribution]

    def test_from_entity(self) -> None:
        entity = entities_factories.DatasetInputFactory.build()
        dataset_form = DatasetForm.from_entity(entity)

        assert dataset_form.title == entity.title
        assert dataset_form.description == entity.description
        assert dataset_form.keyword == entity.keyword
        assert dataset_form.license == entity.license
        assert dataset_form.theme == entity.theme
        assert dataset_form.distribution == [
            Distribution.from_entity(i) for i in entity.distribution
        ]


class TestDatasetImportForm:
    def test_to_entity(self) -> None:
        import_form = DatasetImportFormFactory.build()
        entity = import_form.to_entity()

        assert entity.identifier == import_form.identifier
        assert entity.title == import_form.title
        assert entity.description == import_form.description
        assert entity.keyword == import_form.keyword
        assert entity.license == import_form.license
        assert entity.theme == import_form.theme
        assert entity.catalog == import_form.catalog.to_entity()
        assert entity.distribution == [i.to_entity() for i in import_form.distribution]

    def test_from_entity(self) -> None:
        entity = entities_factories.DatasetImportFactory.build()
        import_form = DatasetImportForm.from_entity(entity)

        assert import_form.identifier == entity.identifier
        assert import_form.title == entity.title
        assert import_form.description == entity.description
        assert import_form.keyword == entity.keyword
        assert import_form.license == entity.license
        assert import_form.theme == entity.theme
        assert import_form.catalog == CatalogImportForm.from_entity(entity.catalog)
        assert import_form.distribution == [
            Distribution.from_entity(i) for i in entity.distribution
        ]
