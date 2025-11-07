from typing import Any, BinaryIO

import json
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import PurePosixPath
from urllib.parse import quote, unquote, urlparse

import httpx
from rdflib import DCAT, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, XSD

from app.core.exceptions import (
    ConnectorError,
    DistributionNotFound,
    InvalidDatasetError,
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
        dataset: Dataset,
        filename: str,
        related_data_product: str,
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
        related_data_product: str,
        context: SaveDatasetContext,
        validator_class: type[IDatasetValidatorService] = DatasetValidatorService,
    ) -> tuple[Dataset, list[str]]:
        """
        Create or update a dataset — full ontology-agnostic version:
          1️ Validate & build MMIO metadata
          2️ Enrich each distribution from connector
          3️ Attach metadata & persist
          4️ Return enriched dataset with clean JSON-LD
        """

        # 1️ Validate dataset structure
        validator = validator_class(
            shacl_url=context["shacl_url"],
            ontology_url=context["ontology_url"],
        )
        validator.validate(dataset)

        # 2️ Load catalog + user info

        catalog = await self.repositories.catalogs.get()
        user = context["user"]
        person = await self._get_or_create_person(user)

        # 3️ Build MMIO metadata
        metadata_items, errors = await self._build_mmio_metadata(
            filename, context["oca_uri"]
        )

        for metadata in metadata_items:
            dataset += metadata  # add triples to RDF graph
            dataset.set_attribute(DSPACE.extraMetadata, metadata.uri)
            catalog += metadata  # ensure persistence

        dataset.set_attribute(DSPACE.metadataFilename, filename)

        # 4 Connector enrichment (extracted to separate method)

        await self._enrich_distributions_with_connector(dataset, related_data_product)

        # 5 Add dataset-level info
        if dataset.get_attribute(DSPACE.isShared) is None:
            dataset.set_attribute(DSPACE.isShared, False)

        dataset.set_attribute(DCTERMS.issued, datetime.now(UTC).isoformat())
        dataset.set_attribute(DSPACE.isDeleted, False)
        dataset.set_attribute(DCTERMS.publisher, person.uri)

        catalog_title = catalog.get_attribute(DCTERMS.title)
        region_value = catalog_title or "Unknown Region"
        dataset.set_attribute(DSPACE.region, region_value)

        # 6 Persist catalog + dataset
        catalog.set_attribute(DCAT.dataset, dataset.uri)
        catalog += dataset
        catalog += person

        await self.repositories.catalogs.save(catalog)

        # 7 Return in-memory enriched dataset (includes extraMetadata)
        return dataset, errors

    async def _enrich_distributions_with_connector(
        self, dataset: Dataset, related_data_product: str
    ) -> None:
        """
        Enrich all distributions in the dataset with connector metadata.
        Handles 404 errors by stopping the flow completely.

        Args:
            dataset: The dataset containing distributions to enrich
            related_data_product: The related folder path for validation

        Raises:
            DistributionNotFound: When connector returns 404
            ConnectorError: When connector returns other error status
            InvalidDatasetError: When distribution lacks required accessURL
        """
        settings = get_settings()
        base_url = settings.connector_base_url.rstrip("/")
        dataset_jsonld = json.loads(dataset.to_json_ld())

        # Find all distribution nodes (ontology-agnostic)
        distribution_nodes: list[URIRef] = []
        for dist_node in dataset.graph.objects(dataset.uri, DCAT.distribution):
            if isinstance(dist_node, URIRef):
                distribution_nodes.append(dist_node)

        for dist_node in distribution_nodes:
            await self._enrich_single_distribution(
                dataset, dist_node, base_url, related_data_product, dataset_jsonld
            )

    async def _enrich_single_distribution(
        self,
        dataset: Dataset,
        dist_node: URIRef,
        base_url: str,
        related_data_product: str,
        dataset_jsonld: dict[str, Any],
    ) -> None:
        """
        Enrich a single distribution with connector metadata.

        Args:
            dataset: The dataset containing the distribution
            dist_node: The URI of the distribution to enrich
            base_url: The connector base URL
            related_data_product: The related folder for path validation
            dataset_jsonld: The dataset JSON-LD representation

        Raises:
            DistributionNotFound: When connector returns 404
            ConnectorError: When connector returns error status
            InvalidDatasetError: When distribution lacks accessURL
        """
        # Extract accessURL
        access_pred = self._expand_iri(
            "dcat:accessURL", dataset_jsonld.get("@context", {})
        )
        access_url = dataset.graph.value(dist_node, URIRef(access_pred))

        if not access_url:
            raise InvalidDatasetError(
                f"No accessURL found for distribution {dist_node}"
            )

        access_url_str = str(access_url)

        # Extract existing distribution data
        existing_data = self._extract_existing_distribution_values(
            dist_node, dataset.graph, dataset_jsonld
        )

        # Parse and validate access URL
        try:
            interface, resource_path = self._parse_access_url(access_url_str)
        except ValueError as e:
            raise InvalidDatasetError(f"Invalid accessURL format: {e}")

        # Validate path is within related folder
        if related_data_product:
            decoded_path = unquote(resource_path)
            if not self._is_child_path(decoded_path, related_data_product):
                raise InvalidDatasetError(
                    f"Access URL '{access_url_str}' path '{decoded_path}' "
                    f"is not inside folder '{related_data_product}'"
                )

        # Call connector API
        connector_url = f"{base_url}/distribution-metadata/{interface}/{resource_path}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(connector_url)

        # Handle connector response
        if response.status_code == 404:
            raise DistributionNotFound(
                f"Distribution metadata not found for access URL {access_url_str}"
            )
        elif not response.is_success:
            raise ConnectorError(
                f"Connector failed with status {response.status_code} "
                f"for {access_url_str}"
            )

        # Extract and merge connector data
        connector_data = response.json().get("distribution", {})

        # Perform ontology-agnostic merge
        self._update_distribution_in_place(
            dataset.graph,
            dist_node,
            connector_data,
            existing_data,
            dataset_jsonld,
        )

    def _parse_access_url(self, file_path: str) -> tuple[str, str]:
        """
        Parses accessURL into (interface, encoded_resource_path).
        Examples:
            file://disease_xyz/images/patient1.dcm →
             ("file", "disease_xyz/images/Fpatient1.dcm")
            file:///data/disease_xyz/images/patient1.dcm →
             ("file", "disease_xyz/Fimages/patient1.dcm")
            s3://bucket/key/file.csv → ("s3", "bucket/Fkey/Ffile.csv")
            https://example.com/data/file.csv  →
            ("http", "https://example.com/data/file.csv")
        """
        settings = get_settings()
        base_path = settings.data_root_path.rstrip("/") + "/"
        parsed = urlparse(file_path)

        if parsed.scheme == "file":
            path_part = file_path.split("://", 1)[-1]

            # If it starts with /data/, trim only that prefix
            if path_part.startswith(base_path):
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
        self,
        graph,
        dist_node,
        connector_data,
        existing_data,
        dataset_jsonld,
    ):
        """
        Ontology-agnostic update of a DCAT Distribution.

        Rules:
        - If connector provides a non-null value => override.
        - If connector provides null and dataset has value => keep dataset.
        - If both connector and dataset have null => explicitly set 'null' (typed).
        - Keep RDF types (URIRefs for URLs, typed literals otherwise).
        - Update nested checksum node correctly (no duplicate checksumValue).
        """

        def add_or_replace_literal(
            subject, predicate, value, dtype=XSD.string, is_uri=False
        ):
            """
            Helper: replace triple or insert new, respecting RDF typing.
            """
            # Remove any existing values first
            graph.remove((subject, predicate, None))

            # 1 Both null => explicit "null"
            if value is None or str(value).lower() in ("none", ""):
                graph.add((subject, predicate, Literal("null", datatype=dtype)))

                return

            # 2 URIs (for URLs)
            if is_uri:
                graph.add((subject, predicate, URIRef(value)))

            else:
                graph.add((subject, predicate, Literal(value, datatype=dtype)))

        # DCAT-AP 3.0.0 field mapping (minimal set)
        field_map = {
            "access_url": (DCAT.accessURL, XSD.anyURI, True),
            "download_url": (DCAT.downloadURL, XSD.anyURI, True),
            "media_type": (DCAT.mediaType, XSD.string, False),
            "package_format": (DCAT.packageFormat, XSD.anyURI, False),
            "format": (DCTERMS.format, XSD.string, False),
            "byte_size": (DCAT.byteSize, XSD.long, False),
            "issued": (DCTERMS.issued, XSD.dateTime, False),
            "modified": (DCTERMS.modified, XSD.dateTime, False),
            "title": (DCTERMS.title, XSD.string, False),
            "description": (DCTERMS.description, XSD.string, False),
            "license": (DCTERMS.license, XSD.string, False),
            "rights": (DCTERMS.rights, XSD.string, False),
            "conforms_to": (DCTERMS.conformsTo, XSD.anyURI, True),
            "access_rights": (DCTERMS.accessRights, XSD.string, False),
            "has_policy": (DCATAP.hasPolicy, XSD.anyURI, True),
            "compress_format": (DCAT.compressFormat, XSD.anyURI, True),
        }

        #  Update fields based on connector
        for field, (predicate, dtype, is_uri) in field_map.items():
            conn_val = connector_data.get(field)
            existing_val = next(iter(graph.objects(dist_node, predicate)), None)

            # Case A: connector has a value -> override
            if conn_val is not None and str(conn_val).lower() not in ("none", ""):
                add_or_replace_literal(dist_node, predicate, conn_val, dtype, is_uri)

            # Case B: connector null, dataset null -> set explicit "null"
            elif existing_val is None:
                add_or_replace_literal(dist_node, predicate, None, dtype, is_uri)

        #  Handle checksum separately (as nested SPDX node)
        checksum_val = connector_data.get("checksum")
        checksum_nodes = list(graph.objects(dist_node, SPDX.checksum))

        if checksum_val is None or str(checksum_val).lower() in ("none", ""):
            # both missing — explicitly write "null" if dataset also had none
            if not checksum_nodes:
                checksum_uri = URIRef(f"{dist_node}/checksum")
                graph.add(
                    (
                        checksum_uri,
                        SPDX.checksumValue,
                        Literal("null", datatype=XSD.hexBinary),
                    )
                )
                graph.add((dist_node, SPDX.checksum, checksum_uri))

        else:
            # connector provided a checksum
            if checksum_nodes:
                checksum_node = checksum_nodes[0]
            else:
                checksum_node = URIRef(f"{dist_node}/checksum")
                graph.add((dist_node, SPDX.checksum, checksum_node))
                graph.add(
                    (
                        checksum_node,
                        SPDX.algorithm,
                        URIRef("http://spdx.org/rdf/terms#SHA256"),
                    )
                )
                graph.add(
                    (
                        checksum_node,
                        SPDX.type,
                        URIRef("http://spdx.org/rdf/terms#Checksum"),
                    )
                )

            graph.remove((checksum_node, SPDX.checksumValue, None))
            graph.add(
                (
                    checksum_node,
                    SPDX.checksumValue,
                    Literal(checksum_val, datatype=XSD.hexBinary),
                )
            )

    def _expand_iri(self, key: str, context: dict[str, Any]) -> str:
        """Enhanced IRI expansion with safe string handling."""
        if ":" in key:
            prefix, local = key.split(":", 1)
            if prefix in context:
                return str(context[prefix]) + local
        if key in context:
            return str(context[key])
        fallback = {
            "title": str(DCTERMS.title),
            "description": str(DCTERMS.description),
            "format": str(DCAT.format),
            "accessURL": str(DCAT.accessURL),
            "downloadURL": str(DCAT.downloadURL),
            "mediaType": str(DCAT.mediaType),
            "byteSize": str(DCAT.byteSize),
            "compressFormat": str(DCAT.compressFormat),
            "packageFormat": str(DCAT.packageFormat),
            "issued": str(DCTERMS.issued),
            "modified": str(DCTERMS.modified),
            "license": str(DCTERMS.license),
            "rights": str(DCTERMS.rights),
            "accessRights": str(DCTERMS.accessRights),
            "accessService": str(DCAT.accessService),
            "conformsTo": str(DCTERMS.conformsTo),
            "hasPolicy": str(DCATAP.hasPolicy),
            "checksum": str(SPDX.checksumValue),
            "checksumValue": str(SPDX.checksumValue),
            "algorithm": str(SPDX.algorithm),
        }
        return fallback.get(key, key)

    def _extract_existing_distribution_values(
        self, dist_node: URIRef, graph: Graph, dataset_jsonld: dict[str, Any]
    ) -> dict[str, str]:
        """Extract all triples for the distribution."""
        existing: dict[str, str] = {}
        for _, p, o in graph.triples((dist_node, None, None)):
            p_str = str(p)
            local_name = p_str.split("#")[-1] if "#" in p_str else p_str.split("/")[-1]
            existing[local_name] = str(o)
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
