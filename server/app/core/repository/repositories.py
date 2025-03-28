from abc import ABC, abstractmethod

from rdflib import DCAT, RDF
from rdflib import Graph as RDFGraph

from app.database import DatabaseDriver

from ..entities import Catalog, Dataset
from ..exceptions import DatasetDoesNotExist, DatasetWasNotSaved, MultipleDatasetsFound
from .neosemantics import Neosemantics
from .queries import Query

# --- Interfaces ---


class IRepository(ABC):
    @abstractmethod
    def __init__(self, db_driver: DatabaseDriver) -> None:
        ...


class IRepositories(ABC):
    @abstractmethod
    def __init__(self, db_driver: DatabaseDriver) -> None:
        ...


class ICatalogRepository(IRepository):
    @abstractmethod
    async def get(self, query: Query) -> Catalog:
        ...


class IDatasetsRepository(IRepository):
    @abstractmethod
    async def get(self, query: Query) -> Dataset:
        ...

    @abstractmethod
    async def save(self, data: Dataset) -> None:
        ...

    @abstractmethod
    async def delete(self, query: Query) -> None:
        ...


# --- Implementations ---


class BaseRepository(IRepository):
    db_driver: DatabaseDriver
    neosemantics: Neosemantics

    def __init__(self, db_driver: DatabaseDriver) -> None:
        self.db_driver = db_driver
        self.neosemantics = Neosemantics(db_driver)


class CatalogRepository(BaseRepository, ICatalogRepository):
    async def get(self, query: Query) -> Catalog:
        q = Query(
            match=[f"({Catalog.label}:dcat__Catalog)-[r*]-(related)"],
            where=['all(rel IN r WHERE type(rel) <> "rdf__type")'],
        )
        q.join(query)
        q.return_clause = [Catalog.label, "r", "related"]
        query_str = q.build()

        graph = await self.neosemantics.export(query_str)
        return Catalog(graph)


class DatasetsRepository(BaseRepository, IDatasetsRepository):
    async def list(self, query: Query) -> list[Dataset]:
        q = Query(
            match=[f"({Dataset.label}:dcat__Dataset)-[r*]-(related)"],
            where=['all(rel IN r WHERE type(rel) <> "rdf__type")'],
        )
        q.join(query)
        q.return_clause = [Dataset.label, "r", "related"]
        query_str = q.build()

        graph = await self.neosemantics.export(query_str)
        if not graph:
            return []

        datasets = []
        for dataset_uri in graph.subjects(RDF.type, DCAT.Dataset):
            dataset_graph = RDFGraph()
            for triple in graph.triples((dataset_uri, None, None)):
                dataset_graph.add(triple)
            datasets.append(Dataset(dataset_graph))

        return datasets

    async def get(self, query: Query) -> Dataset:
        result = await self.list(query)
        if not result:
            raise DatasetDoesNotExist("Dataset not found in the graph")
        if len(result) > 1:
            raise MultipleDatasetsFound("Multiple datasets found in the graph")
        return result[0]

    async def save(self, dataset: Dataset) -> None:
        result = await self.neosemantics.save(dataset.graph)
        if result["triples_loaded"] == 0:
            raise DatasetWasNotSaved("Dataset was not saved in the database")

    async def delete(self, query: Query) -> None:
        q = Query(
            match=[f"({Dataset.label}:dcat__Dataset)-[r*]-(related)"],
            where=['all(rel IN r WHERE type(rel) <> "rdf__type")'],
        )
        q.join(query)
        query_str = q.build()
        query_str += f"""
            UNWIND r AS rel
            DELETE rel
            WITH {Dataset.label}, collect(related) AS nodes
            UNWIND nodes AS node
            DETACH DELETE node
            DETACH DELETE {Dataset.label}
            RETURN COUNT(*) AS deleted_count
        """

        result = await self.db_driver.execute_query(
            query_str, result_transformer_=lambda r: r.single(strict=True)
        )

        if result["deleted_count"] == 0:
            raise DatasetDoesNotExist("Dataset not found in the graph")


# --- Repositories class ---


class Repositories(IRepositories):
    def __init__(self, db_driver: DatabaseDriver) -> None:
        self.catalog = CatalogRepository(db_driver)
        self.datasets = DatasetsRepository(db_driver)
