from typing import Generic, TypeVar

from abc import ABC, abstractmethod

from rdflib import DCAT, FOAF, RDF

from app.database import DatabaseDriver

from ..entities import Catalog, Dataset, Graph, Person
from ..exceptions import ErrorSavingData, MultipleNodesFound, NodeDoesNotExist
from ..namespace import DSPACE
from .neosemantics import Neosemantics
from .queries import Query

# --- Interfaces ---


T = TypeVar("T", bound=Graph)


class IRepository(ABC, Generic[T]):
    @abstractmethod
    def __init__(self, db_driver: DatabaseDriver) -> None:
        ...

    @abstractmethod
    async def save(self, obj: T) -> None:
        ...


class IRepositories(ABC):
    @abstractmethod
    def __init__(self, db_driver: DatabaseDriver) -> None:
        ...


class IPersonsRepository(IRepository[Person]):
    @abstractmethod
    async def get(self, query: Query) -> Person:
        ...


class ICatalogsRepository(IRepository[Catalog]):
    @abstractmethod
    async def create(self, title: str, description: str) -> Catalog:
        ...

    @abstractmethod
    async def get(self, query: Query | None = None) -> Catalog:
        ...


class IDatasetsRepository(IRepository[Dataset]):
    @abstractmethod
    async def get(self, query: Query) -> Dataset:
        ...

    @abstractmethod
    async def delete(self, query: Query) -> None:
        ...


# --- Implementations ---


class BaseRepository(IRepository[T], Generic[T]):
    db_driver: DatabaseDriver
    neosemantics: Neosemantics

    def __init__(self, db_driver: DatabaseDriver) -> None:
        self.db_driver = db_driver
        self.neosemantics = Neosemantics(db_driver)

    async def save(self, obj: T) -> None:
        result = await self.neosemantics.save(obj.graph)
        if not result["success"]:
            message = result["extra_info"]
            raise ErrorSavingData(f"Graph was not saved: {message}")


class PersonsRepository(BaseRepository[Person], IPersonsRepository):
    async def get(self, query: Query) -> Person:
        p = Person.label

        q = Query(
            match=[f"({p}:foaf__Person)-[r*0..]->(related)"],
            where=['all(rel IN r WHERE type(rel) <> "rdf__type")'],
        )
        q += query
        q.return_clause = [p, "r", "related"]
        query_str = q.build()

        graph = await self.neosemantics.export(query_str)
        if not graph:
            raise NodeDoesNotExist("Person not found in the graph")
        if len(list(graph.subjects(RDF.type, FOAF.Person))) > 1:
            raise MultipleNodesFound("Multiple persons found in the graph")

        return Person(graph)


class CatalogsRepository(BaseRepository[Catalog], ICatalogsRepository):
    async def create(self, title: str, description: str) -> Catalog:
        catalog = Catalog.create(title, description)
        await self.neosemantics.save(catalog.graph)
        return catalog

    async def get(self, query: Query | None = None) -> Catalog:
        c = Catalog.label
        d = Dataset.label

        q1 = Query(
            match=[f"({c}:dcat__Catalog)"],
            optional_match=[f"({c})-[dataset_rel:dcat__dataset]->({d}:dcat__Dataset)"],
            where=[f"{d}.dspace__isDeleted<>true"],
        )

        q2 = Query(
            optional_match=[f"({d})-[r*0..]->(related)"],
            where=['all(rel IN r WHERE type(rel) <> "rdf__type")'],
        )
        if query is not None:
            q2 += query
        q2.return_clause = [c, "dataset_rel", d, "r", "related"]

        query_str = q1.build_together(q2)

        graph = await self.neosemantics.export(query_str)
        if not graph:
            raise NodeDoesNotExist("Catalog not found in the graph")
        if len(list(graph.subjects(RDF.type, DCAT.Catalog))) > 1:
            raise MultipleNodesFound("Multiple catalogs found in the graph")

        return Catalog(graph)


class DatasetsRepository(BaseRepository[Dataset], IDatasetsRepository):
    async def get(self, query: Query) -> Dataset:
        d = Dataset.label

        q = Query(
            match=[f"({d}:dcat__Dataset)-[r*0..]->(related)"],
            where=['all(rel IN r WHERE type(rel) <> "rdf__type")'],
        )
        q.add_where(f"{d}.dspace__isDeleted<>true")
        q += query
        q.return_clause = [d, "r", "related"]
        query_str = q.build()

        graph = await self.neosemantics.export(query_str)
        if not graph:
            raise NodeDoesNotExist("Dataset not found in the graph")
        if len(list(graph.subjects(RDF.type, DCAT.Dataset))) > 1:
            raise MultipleNodesFound("Multiple datasets found in the graph")

        return Dataset(graph)

    async def delete(self, query: Query) -> None:
        dataset = await self.get(query)
        dataset.set_attribute(DSPACE.isDeleted, True)
        await self.save(dataset)


# --- Repositories class ---


class Repositories(IRepositories):
    def __init__(self, db_driver: DatabaseDriver) -> None:
        self.persons = PersonsRepository(db_driver)
        self.catalogs = CatalogsRepository(db_driver)
        self.datasets = DatasetsRepository(db_driver)
