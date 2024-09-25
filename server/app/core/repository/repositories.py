from typing import Generic, TypeVar, cast

from abc import ABC, abstractmethod

from neomodel import db

from ..entities import Checksum, DataService, Dataset, Distribution, NewDataset, Person
from ..exceptions import DatasetDoesNotExist
from .models import (
    CatalogNode,
    ChecksumNode,
    DataServiceNode,
    DatasetNode,
    DistributionNode,
    PersonNode,
)
from .queries import IQuery

TEntity = TypeVar("TEntity")
TNewEntity = TypeVar("TNewEntity")


class IRepository(ABC, Generic[TEntity, TNewEntity]):
    @abstractmethod
    async def list(self, query: IQuery) -> list[TEntity]:
        ...

    @abstractmethod
    async def get(self, query: IQuery) -> TEntity:
        ...

    @abstractmethod
    async def exists(self, query: IQuery) -> bool:
        ...

    @abstractmethod
    async def create(self, data: TNewEntity) -> TEntity:
        ...

    @abstractmethod
    async def update(self, entity: TEntity) -> TEntity:
        ...

    @abstractmethod
    async def delete(self, entity: TEntity) -> None:
        ...


class ICatalogItemRepository(IRepository[Dataset, NewDataset]):
    ...


class CatalogItemRepository(ICatalogItemRepository):
    async def list(self, query: IQuery) -> list[Dataset]:
        # TODO: Optimize nested queries to the database
        nodes = await query.apply(DatasetNode.nodes)
        entities = []
        for node in nodes:
            entity = await self._to_entity(node)
            entities.append(entity)
        return entities

    async def get(self, query: IQuery) -> Dataset:
        try:
            node = await query.apply(DatasetNode.nodes).first()
            return await self._to_entity(node)
        except DatasetNode.DoesNotExist as err:
            raise DatasetDoesNotExist(err)

    async def exists(self, query: IQuery) -> bool:
        try:
            await query.apply(DatasetNode.nodes).first()
            return True
        except DatasetNode.DoesNotExist:
            return False

    async def create(self, dataset_entity: NewDataset) -> Dataset:
        with db.transaction:
            dataset_node = DatasetNode()
            dataset_fields = dataset_entity.model_dump(
                exclude=set(["creator", "distribution"])
            )
            for field_name, value in dataset_fields.items():
                setattr(dataset_node, field_name, value)
            await dataset_node.save()

            creator_entity = dataset_entity.creator
            creator_node, _ = await self._get_or_create_person(creator_entity)
            await dataset_node.creator.connect(creator_node)

            catalog_node, is_created = await self._get_or_create_catalog(creator_entity)
            if is_created:
                await catalog_node.creator.connect(creator_node)

            await catalog_node.dataset.connect(dataset_node)

            await self._create_related_nodes(dataset_entity, dataset_node, catalog_node)

        return await self._to_entity(dataset_node)

    async def update(self, dataset_entity: Dataset) -> Dataset:
        with db.transaction:
            dataset_node = await self._get_node(dataset_entity)

            dataset_fields = dataset_entity.model_dump(
                exclude=set(["creator", "distribution"])
            )
            for field_name, value in dataset_fields.items():
                setattr(dataset_node, field_name, value)
            await dataset_node.save()

            creator_entity = dataset_entity.creator
            creator_node, _ = await self._get_or_create_person(creator_entity)
            current_creator = await dataset_node.creator.get()
            if current_creator != creator_node:
                await dataset_node.creator.reconnect(current_creator, creator_node)

            catalog_node, is_created = await self._get_or_create_catalog(creator_entity)
            if is_created:
                await catalog_node.creator.connect(creator_node)

            current_catalog = await dataset_node.catalog.get()
            if current_catalog != catalog_node:
                await current_catalog.dataset.disconnect(dataset_node)
                await catalog_node.dataset.connect(dataset_node)

            await self._delete_related_nodes(dataset_node)
            await self._create_related_nodes(dataset_entity, dataset_node, catalog_node)

        return await self._to_entity(dataset_node)

    async def delete(self, dataset_entity: Dataset) -> None:
        with db.transaction:
            dataset_node = await self._get_node(dataset_entity)
            await self._delete_related_nodes(dataset_node)
            await dataset_node.delete()

    async def _to_entity(self, dataset_node: DatasetNode) -> Dataset:
        # TODO: Optimize nested queries to the database

        creator_node = await dataset_node.creator.get()
        creator_entity = Person(
            id=creator_node.identifier,
            name=creator_node.name,
        )

        distribution_nodes = await dataset_node.distribution.all()
        distribution_entities = []
        for distribution_node in distribution_nodes:
            checksum_node = await distribution_node.checksum.get()
            checksum_entity = Checksum(
                algorithm=checksum_node.algorithm,
                checksum_value=checksum_node.checksum_value,
            )

            service_nodes = await distribution_node.access_service.all()
            service_entities = []
            for service_node in service_nodes:
                service_entity = DataService(endpoint_url=service_node.endpoint_url)
                service_entities.append(service_entity)

            distribution_entities.append(
                Distribution(
                    byte_size=distribution_node.byte_size,
                    media_type=distribution_node.media_type,
                    checksum=checksum_entity,
                    access_service=service_entities,
                )
            )

        return Dataset(
            identifier=dataset_node.identifier,
            title=dataset_node.title,
            description=dataset_node.description,
            keyword=dataset_node.keyword,
            license=dataset_node.license,
            is_local=dataset_node.is_local,
            is_shared=dataset_node.is_shared,
            issued=dataset_node.issued,
            theme=dataset_node.theme,
            creator=creator_entity,
            distribution=distribution_entities,
        )

    async def _get_or_create_person(
        self, person_entity: Person
    ) -> tuple[PersonNode, bool]:
        is_created = False
        person_node = await PersonNode.nodes.get_or_none(identifier=person_entity.id)
        if person_node is None:
            is_created = True
            person_node = await PersonNode(
                identifier=person_entity.id,
                name=person_entity.name,
            ).save()
        return person_node, is_created

    async def _get_or_create_catalog(self, creator: Person) -> tuple[CatalogNode, bool]:
        identifier = f"{creator.id}_catalog"
        catalog = await CatalogNode.nodes.get_or_none(identifier=identifier)
        if catalog is not None:
            return catalog, False
        return await CatalogNode(identifier=identifier).save(), True

    async def _get_node(self, dataset_entity: Dataset) -> DatasetNode:
        try:
            node = await DatasetNode.nodes.get(identifier=dataset_entity.identifier)
            return cast(DatasetNode, node)
        except DatasetNode.DoesNotExist as err:
            raise DatasetDoesNotExist(err)

    async def _delete_related_nodes(self, dataset_node: DatasetNode) -> None:
        distribution_nodes = await dataset_node.distribution.all()
        for distribution_node in distribution_nodes:
            checksum_node = await distribution_node.checksum.get()
            await checksum_node.delete()

            service_nodes = await distribution_node.access_service.all()
            for service_node in service_nodes:
                await service_node.delete()

            await distribution_node.delete()

    async def _create_related_nodes(self, dataset_entity, dataset_node, catalog_node):
        for distribution_entity in dataset_entity.distribution:
            distribution_node = await DistributionNode(
                byte_size=distribution_entity.byte_size,
                media_type=distribution_entity.media_type,
            ).save()

            checksum_node = await ChecksumNode(
                algorithm=distribution_entity.checksum.algorithm,
                checksum_value=distribution_entity.checksum.checksum_value,
            ).save()
            await distribution_node.checksum.connect(checksum_node)

            for service_entity in distribution_entity.access_service:
                service_node = await DataServiceNode(
                    endpoint_url=service_entity.endpoint_url,
                ).save()

                await distribution_node.access_service.connect(service_node)
                await catalog_node.service.connect(service_node)
                await service_node.serves_dataset.connect(dataset_node)

            await dataset_node.distribution.connect(distribution_node)


catalog_item_repo = CatalogItemRepository()
