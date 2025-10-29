from typing import BinaryIO, cast

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import PurePosixPath
from urllib.parse import quote, unquote, urlparse

import httpx
from rdflib import DCAT, RDF, Literal, URIRef
from rdflib.graph import Graph as RDFGraph
from rdflib.namespace import DCTERMS, XSD

from app.core.exceptions import (
    ConnectorError,
    DistributionNotFound,
    NodeDoesNotExist,
    QueryIsRequired,
)

from ..settings import get_settings
from .context import Context, SaveDatasetContext
from .entities import Catalog, CatalogFilters, Dataset, Metadata, Person, User
from .mmio import (
    MMIO,
    IMMIOParser,
    JsonMMIOParser,
    TarMMIOParser,
    mmio_available_attrs,
    mmio_data_to_entities,
)
from .namespace import DCATAP, DSPACE, SPDX
from .repository import Repositories
from .repository.queries import FilterDatasetByID, FilterPersonByID
from .repository.query_builder import catalog_filter_to_query, uri_to_cypher
from .validators import (
    CatalogFiltersValidatorService,
    DatasetValidatorService,
    IDatasetValidatorService,
    IValidatorService,
)

connector_file_path = None


class IUsecases(ABC):
    def __init__(self, repositories: Repositories) -> None:
        ...


class BaseUsecases(IUsecases):
    def __init__(self, repositories: Repositories) -> None:
        self.repositories = repositories


# --- Interfaces ---


class ICatalogUsecases(IUsecases):
    @abstractmethod
    async def get_local_catalog(
        self, filters: CatalogFilters, context: Context
    ) -> Catalog:
        ...


class IDatasetsUsecases(IUsecases):
    @abstractmethod
    async def save(
        self,
        data: Dataset,
        filename: str,
        context: SaveDatasetContext,
        validator_class: type[IDatasetValidatorService],
    ) -> tuple[Dataset, list[str]]:
        ...

    @abstractmethod
    async def get(self, id: str, context: Context) -> Dataset:
        ...

    @abstractmethod
    async def delete(self, id: str, context: Context) -> None:
        ...


class IDatasetSharingUsecases(IUsecases):
    @abstractmethod
    async def share(self, id: str, context: Context) -> None:
        ...

    @abstractmethod
    async def unshare(self, id: str, context: Context) -> None:
        ...


class IMMIOsUsecases(IUsecases):
    @abstractmethod
    async def create(self, file: BinaryIO, filename: str, context: Context) -> None:
        ...

    @abstractmethod
    async def get(self, filename: str, context: Context) -> str:
        ...

    @abstractmethod
    async def delete(self, filename: str, context: Context) -> None:
        ...


# --- Implementations ---


class CatalogUsecases(BaseUsecases, ICatalogUsecases):
    async def get_local_catalog(
        self,
        filters: CatalogFilters,
        context: Context,
        validator_class: type[IValidatorService] = CatalogFiltersValidatorService,
    ) -> Catalog:
        """Get the local catalog"""

        validator = validator_class()
        validator.validate(filters)

        namespaces = await self.repositories.get_namespaces()
        query = catalog_filter_to_query(filters, namespaces)
        return await self.repositories.catalogs.get(query)

    async def get_public_catalog(
        self,
        filters: CatalogFilters,
        context: Context,
        validator_class: type[IValidatorService] = CatalogFiltersValidatorService,
    ) -> Catalog:
        """Get the public catalog"""

        validator = validator_class()
        validator.validate(filters)

        namespaces = await self.repositories.get_namespaces()
        query = catalog_filter_to_query(filters, namespaces)
        if query is None:
            raise QueryIsRequired("Query is required for public catalog")

        is_shared_attr_name = uri_to_cypher(DSPACE.isShared, namespaces)
        query.add_where(f"{Dataset.label}.{is_shared_attr_name}=true")

        return await self.repositories.catalogs.get(query)


class DatasetsUsecases(BaseUsecases, IDatasetsUsecases):
    async def save(
        self,
        dataset: Dataset,
        filename: str,
        context: SaveDatasetContext,
        validator_class: type[IDatasetValidatorService] = DatasetValidatorService,
    ) -> tuple[Dataset, list[str]]:
        """Create or update a dataset — with connector enrichment (in-place update)."""

        # 1 Validate dataset
        validator = validator_class(
            shacl_url=context["shacl_url"],
            ontology_url=context["ontology_url"],
        )
        validator.validate(dataset)

        # 2 Get catalog + user
        catalog = await self.repositories.catalogs.get()
        user = context["user"]
        person = await self._get_or_create_person(user)

        # 3 Add MMIO metadata
        metadata_items, errors = await self._build_mmio_metadata(
            filename, context["oca_uri"]
        )

        for metadata in metadata_items:
            dataset += metadata
            dataset.set_attribute(DSPACE.extraMetadata, metadata.uri)
        dataset.set_attribute(DSPACE.metadataFilename, filename)

        # 4 Connector integration BEFORE saving

        print("=== Connector Integration (In-Place Update) ===")

        settings = get_settings()
        base_url = settings.connector_base_url.rstrip("/")
        related_folder = context.get("related_data_product")

        # Loop through existing distributions
        for dist_node in list(dataset.graph.objects(dataset.uri, DCAT.distribution)):
            access_url = dataset.graph.value(dist_node, DCAT.accessURL)
            if not access_url:
                continue

            access_url_str = str(access_url)
            existing_data = self._extract_existing_distribution_values(
                cast(URIRef, dist_node), dataset.graph
            )
            connector_data = {}

            # Parse accessURL (protocol + resource path)
            try:
                interface, resource_path = self._parse_access_url(access_url_str)
            except ValueError as e:
                print(f" Invalid accessURL format: {access_url_str} ({e})")
                continue

            # Validate: distribution path must be inside the related folder
            if related_folder:
                decoded_path = unquote(resource_path)
                if not self._is_child_path(decoded_path, related_folder):
                    raise ValueError(
                        f"Access URL '{access_url_str}', path '{decoded_path}' "
                        f"is not inside the related data product "
                        f"folder '{related_folder}'."
                    )

            # Build connector URL
            connector_url = (
                f"{base_url}/distribution-metadata/{interface}/{resource_path}"
            )
            print(f"Fetching connector metadata from {connector_url}")

            # Fetch metadata from connector
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(connector_url)

            if response.is_success:
                connector_json = response.json()
                connector_data = connector_json.get("distribution", {})
                print(f" Connector data merged for {access_url}")
            elif response.status_code == 404:
                # print(f"Access URL not found in connector: {access_url_str}")
                raise DistributionNotFound(
                    f"Access URL not found in connector: {access_url_str}"
                )
            else:
                raise ConnectorError(
                    f"Connector returned {response.status_code} for {access_url_str}"
                )

            # Merge connector values in-place
            self._update_distribution_in_place(
                dataset.graph, dist_node, connector_data, existing_data
            )

        print("=== Finished in-place merge of distributions ===")

        # Add dataset-level metadata
        is_shared = dataset.get_attribute(DSPACE.isShared)
        if is_shared is None:
            dataset.set_attribute(DSPACE.isShared, False)
        dataset.set_attribute(DCTERMS.issued, datetime.now(UTC).isoformat())
        dataset.set_attribute(DSPACE.isDeleted, False)
        dataset.set_attribute(DCTERMS.publisher, person.uri)

        # Link dataset to catalog and save
        catalog.set_attribute(DCAT.dataset, dataset.uri)
        catalog += dataset
        catalog += person

        print("Saving catalog and dataset to Neo4j (after connector merge)...")
        await self.repositories.catalogs.save(catalog)

        #  Return updated dataset
        dataset_id = dataset.get_attribute(DCTERMS.identifier)
        final_dataset = await self.get(dataset_id, context)
        return final_dataset, errors

    def _parse_access_url(self, file_path: str) -> tuple[str, str]:
        """
        Parses accessURL into (interface, encoded_resource_path).
        Examples:
            file://disease_xyz/images/patient1.dcm →
             ("file", "disease_xyz/images/Fpatient1.dcm")
            file:///data/disease_xyz/images/patient1.dcm →
             ("file", "disease_xyz/Fimages/patient1.dcm")
            s3://bucket/key/file.csv → ("s3", "bucket/Fkey/Ffile.csv")
            https://example.com/data/file.csv →
            ("http", "https://example.com/data/file.csv")
        """

        parsed = urlparse(file_path)

        if parsed.scheme == "file":
            path_part = file_path.split("://", 1)[-1]

            # If it starts with /data/, trim only that prefix
            if path_part.startswith("/data/"):
                path_part = path_part[len("/data/") :]
            elif path_part.startswith("/"):
                path_part = path_part[1:]

            normalized = path_part.strip("/")
            encoded = quote(normalized, safe="")
            return "file", encoded

        elif parsed.scheme == "s3":
            bucket = parsed.netloc
            key = parsed.path.lstrip("/")
            normalized = f"{bucket}/{key}"
            encoded = quote(normalized, safe="")
            return "s3", encoded

        elif parsed.scheme in ["http", "https"]:
            return "http", file_path
        else:
            raise ValueError(f"Unsupported URI scheme: {parsed.scheme or 'unknown'}")

    def _is_child_path(self, resource_path: str, related_folder: str) -> bool:
        """
        Check if resource_path (normalized, no scheme) is inside related_folder.
        Works for both relative and absolute paths.
        Example:
            resource_path = "disease_xyz/images/patient1.dcm"
            related_folder = "disease_xyz"
        Returns: True
        """
        # Normalize both paths (remove URL encoding if needed)
        resource_path = resource_path.strip("/")
        related_folder = related_folder.strip("/")

        # Compare using pathlib, which handles "../" etc cleanly
        resource_parts = PurePosixPath(resource_path).parts
        folder_parts = PurePosixPath(related_folder).parts

        # Must start with the folder parts
        return resource_parts[: len(folder_parts)] == folder_parts

    def _update_distribution_in_place(
        self, graph, dist_node, connector_data, existing_data
    ):
        """Update existing RDF distribution node in
        place using connector + dataset data."""

        def choose(conn_key, exist_key=None):
            exist_key = exist_key or conn_key
            conn_val = connector_data.get(conn_key)
            if conn_val not in [None, "", "null"]:
                return conn_val
            exist_val = existing_data.get(exist_key)
            if exist_val not in [None, "", "null"]:
                return exist_val
            return None

        def set_or_update(predicate, value, datatype=None):
            if value is not None:
                graph.remove((dist_node, predicate, None))
                graph.add(
                    (
                        dist_node,
                        predicate,
                        Literal(value, datatype=datatype)
                        if datatype
                        else Literal(value),
                    )
                )

        # Core DCAT/DCAT-AP/DC Terms fields
        set_or_update(DCTERMS.title, choose("title"))
        set_or_update(DCTERMS.description, choose("description"))
        set_or_update(DCAT.accessURL, choose("access_url", "accessURL"))
        set_or_update(DCAT.downloadURL, choose("download_url", "downloadURL"))
        set_or_update(DCAT.mediaType, choose("media_type", "mediaType"))
        set_or_update(DCTERMS.format, choose("format"))
        set_or_update(DCTERMS.license, choose("license"))
        set_or_update(
            DCAT.byteSize, choose("byte_size", "byteSize"), XSD.nonNegativeInteger
        )
        set_or_update(DCAT.accessService, choose("access_service"))
        set_or_update(DCAT.compressFormat, choose("compress_format"))
        set_or_update(DCAT.packageFormat, choose("package_format"))
        set_or_update(DCTERMS.accessRights, choose("access_rights"))
        set_or_update(DCTERMS.conformsTo, choose("conforms_to"))
        set_or_update(DCTERMS.issued, choose("issued"))
        set_or_update(DCTERMS.modified, choose("modified"))
        set_or_update(DCTERMS.rights, choose("rights"))
        set_or_update(DCATAP.hasPolicy, choose("has_policy"))
        set_or_update(DSPACE.region, choose("region"))

        # SPDX Checksum handling
        checksum = choose("checksum", "checksumValue")
        if checksum:
            checksum_uri = URIRef(f"{dist_node}/checksum")
            graph.remove((dist_node, SPDX.checksum, None))
            graph.add((checksum_uri, RDF.type, SPDX.Checksum))
            graph.add(
                (
                    checksum_uri,
                    SPDX.checksumValue,
                    Literal(checksum, datatype=XSD.hexBinary),
                )
            )
            graph.add((checksum_uri, SPDX.algorithm, SPDX.SHA256))
            graph.add((dist_node, SPDX.checksum, checksum_uri))

    # Add this method to the DatasetsUsecases class
    def _extract_existing_distribution_values(
        self, dist_node: URIRef, graph: RDFGraph
    ) -> dict[str, str]:
        """Extract existing distribution values for fallback"""
        existing = {}

        # Core properties
        if title := graph.value(dist_node, DCTERMS.title):
            existing["title"] = str(title)
        if desc := graph.value(dist_node, DCTERMS.description):
            existing["description"] = str(desc)
        if access_url := graph.value(dist_node, DCAT.accessURL):
            existing["accessURL"] = str(access_url)
        if download_url := graph.value(dist_node, DCAT.downloadURL):
            existing["downloadURL"] = str(download_url)
        if media_type := graph.value(dist_node, DCAT.mediaType):
            existing["mediaType"] = str(media_type)
        if format_val := graph.value(dist_node, DCTERMS.format):
            existing["format"] = str(format_val)
        if license_val := graph.value(dist_node, DCTERMS.license):
            existing["license"] = str(license_val)
        if byte_size := graph.value(dist_node, DCAT.byteSize):
            existing["byteSize"] = str(byte_size)

        # Additional properties
        if access_service := graph.value(dist_node, DCAT.accessService):
            existing["access_service"] = str(access_service)
        if compress_format := graph.value(dist_node, DCAT.compressFormat):
            existing["compress_format"] = str(compress_format)
        if package_format := graph.value(dist_node, DCAT.packageFormat):
            existing["package_format"] = str(package_format)
        if access_rights := graph.value(dist_node, DCTERMS.accessRights):
            existing["access_rights"] = str(access_rights)
        if conforms_to := graph.value(dist_node, DCTERMS.conformsTo):
            existing["conforms_to"] = str(conforms_to)
        if issued := graph.value(dist_node, DCTERMS.issued):
            existing["issued"] = str(issued)
        if modified := graph.value(dist_node, DCTERMS.modified):
            existing["modified"] = str(modified)
        if rights := graph.value(dist_node, DCTERMS.rights):
            existing["rights"] = str(rights)
        if has_policy := graph.value(dist_node, DCATAP.hasPolicy):
            existing["has_policy"] = str(has_policy)

        # Handle checksum
        checksum_node = graph.value(dist_node, SPDX.checksum)
        if checksum_node:
            if checksum_val := graph.value(checksum_node, SPDX.checksumValue):
                existing["checksumValue"] = str(checksum_val)

        return existing

    async def _build_mmio_metadata(
        self, filename: str, schema_uri: str
    ) -> tuple[list[Metadata], list[str]]:
        mmio_bytes = await self.repositories.files.read(filename)
        parser: IMMIOParser
        if filename.endswith(".tar"):
            parser = TarMMIOParser()
        else:
            parser = JsonMMIOParser()
        mmio = MMIO(mmio_bytes, parser=parser, schema_uri=schema_uri)
        mmio = mmio.transform_to(schema_uri)
        data = mmio_available_attrs(mmio)
        metadata = mmio_data_to_entities(schema_uri, mmio.id, data)

        return metadata, getattr(parser, "errors", [])

    async def get(self, id: str, context: Context) -> Dataset:
        """Get a dataset by its ID"""
        query = FilterDatasetByID(id)
        return await self.repositories.datasets.get(query)

    async def delete(self, id: str, context: Context) -> None:
        """Delete a dataset by its ID"""
        query = FilterDatasetByID(id)
        await self.repositories.datasets.delete(query)

    async def _get_or_create_person(self, user: User) -> Person:
        query = FilterPersonByID(user["id"])
        try:
            person = await self.repositories.persons.get(query)
        except NodeDoesNotExist:
            person = Person.from_user(user)
        return person


class DatasetSharingUsecases(BaseUsecases, IDatasetSharingUsecases):
    async def share(self, id: str, context: Context) -> None:
        """Share a dataset"""
        query = FilterDatasetByID(id)
        dataset = await self.repositories.datasets.get(query)
        dataset.set_attribute(DSPACE.isShared, True)
        await self.repositories.datasets.save(dataset)

    async def unshare(self, id: str, context: Context) -> None:
        """Unshare a dataset"""
        query = FilterDatasetByID(id)
        dataset = await self.repositories.datasets.get(query)
        dataset.set_attribute(DSPACE.isShared, False)
        await self.repositories.datasets.save(dataset)


class MMIOsUsecases(BaseUsecases, IMMIOsUsecases):
    async def create(self, file: BinaryIO, filename: str, context: Context) -> None:
        """Create a new MMIO file"""
        await self.repositories.files.create(file, filename)

    async def get(self, filename: str, context: Context) -> str:
        """Get a MMIO file"""
        return await self.repositories.files.get_file_path(filename)

    async def delete(self, filename: str, context: Context) -> None:
        """Delete a MMIO file"""
        await self.repositories.files.delete(filename)
