from typing import BinaryIO, Generic, TypeVar

from abc import ABC, abstractmethod
from pathlib import Path

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

    @abstractmethod
    async def get_namespaces(self) -> dict[str, str]:
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


class IFilesRepository(ABC):
    @abstractmethod
    def __init__(self, upload_folder: str) -> None:
        ...

    @abstractmethod
    async def create(self, file: BinaryIO, filename: str) -> None:
        ...

    @abstractmethod
    async def get_file_path(self, filename: str) -> str:
        ...

    @abstractmethod
    async def delete(self, filename: str) -> None:
        ...

    @abstractmethod
    async def read(self, filename: str) -> bytes:
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

        q = Query(
            match=[f"({c}:dcat__Catalog)"],
            optional_match=[f"({c})-[r0:dcat__dataset]->({d})-[r*0..]->(related)"],
            where=[
                'all(rel IN r WHERE type(rel) <> "rdf__type")',
                f"{d}.dspace__isDeleted<>true",
            ],
            return_clause=[c, "r0", d, "r", "related"],
        )

        if query is None:
            query_str = q.build()
        else:
            query_str = Query.build_together(query, q)

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


class FilesRepository(IFilesRepository):
    _upload_folder: Path

    def __init__(self, upload_folder: str = "./uploads") -> None:
        self._upload_folder = Path(upload_folder)
        self._upload_folder.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, filename: str) -> Path:
        return self._upload_folder / filename.lower()

    async def create(self, file: BinaryIO, filename: str) -> None:
        file_path = self._get_file_path(filename)
        # if file_path.exists():
        #     raise FileExistsError(f"File {filename} already exists")
        with file_path.open("wb") as f:
            f.write(file.read())

    async def get_file_path(self, filename: str) -> str:
        file_path = self._get_file_path(filename)
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
        return str(file_path)

    async def delete(self, filename: str) -> None:
        file_path = self._get_file_path(filename)
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
        file_path.unlink()

    async def read(self, filename: str) -> bytes:
        file_path = self._get_file_path(filename)
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
        return file_path.read_bytes()

    async def exists(self, filename: str) -> bool:
        file_path = self._get_file_path(filename)
        return file_path.exists()


# --- Repositories class ---


class Repositories(IRepositories):
    def __init__(self, db_driver: DatabaseDriver) -> None:
        self.db_driver = db_driver
        self.neosemantics = Neosemantics(db_driver)

        self.persons = PersonsRepository(db_driver)
        self.catalogs = CatalogsRepository(db_driver)
        self.datasets = DatasetsRepository(db_driver)
        self.files = FilesRepository()

    async def get_namespaces(self) -> dict[str, str]:
        return await self.neosemantics.list_namespaces()
