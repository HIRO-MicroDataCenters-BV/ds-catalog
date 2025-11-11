# server/app/core/connector_integration.py
from typing import Any

import json
from pathlib import PurePosixPath
from urllib.parse import quote, unquote, urlparse

import httpx
from rdflib import XSD, Graph, Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS

from ..settings import get_settings
from .entities import Dataset
from .exceptions import ConnectorError, DistributionNotFound, InvalidDatasetError
from .namespace import DCATAP, SPDX


class ConnectorIntegration:
    """
    A mixin class providing methods for enriching DCAT Distributions
    with connector metadata.
    """

    async def enrich_distributions_with_connector(
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
        print(
            "******************[debug] ✅ Enriched distribution ",
            list(dataset.graph.objects(dist_node, DCTERMS.format)),
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
            """Helper: replace triple or insert new, respecting RDF typing."""
            graph.remove((subject, predicate, None))

            if value is None or str(value).lower() in ("none", ""):
                graph.add((subject, predicate, Literal("null", datatype=dtype)))
                return

            if is_uri:
                graph.add((subject, predicate, URIRef(value)))
            else:
                graph.add((subject, predicate, Literal(value, datatype=dtype)))

        # --- Load field mapping from configuration file ---
        import json
        from pathlib import Path

        config_path = Path(__file__).parent / "field_map_config.json"
        print(f"[DEBUG] Loading field map config from: {config_path}")

        with open(config_path, encoding="utf-8") as f:
            raw = json.load(f)

        field_map: dict[str, Any] = {}
        for key, value in raw.items():
            if isinstance(value, list):
                # Simple field (3 values)
                uri_str, dtype_uri, is_uri = value
                field_map[key] = (
                    URIRef(uri_str),
                    getattr(XSD, dtype_uri),
                    bool(is_uri),
                )
            elif isinstance(value, dict):
                # Complex field (like checksum)
                field_map[key] = {
                    "predicate": URIRef(value["predicate"]),
                    "nested_predicate": URIRef(value["nested_predicate"]),
                    "datatype": getattr(XSD, value["datatype"].split("#")[-1])
                    if "#" in value["datatype"]
                    else getattr(XSD, value["datatype"]),
                    "is_uri": bool(value.get("is_uri", False)),
                    "nested_is_uri": bool(value.get("nested_is_uri", False)),
                }

        print(f"[DEBUG] Starting connector update for distribution: {dist_node}")

        # --- Update regular fields from connector ---
        for field, mapping in field_map.items():
            if isinstance(mapping, dict):  # skip nested ones (like checksum)
                continue

            predicate, dtype, is_uri = mapping
            conn_val = connector_data.get(field)
            existing_val = next(iter(graph.objects(dist_node, predicate)), None)

            print(f"[DEBUG] Field '{field}':")
            print(f"    Predicate: {predicate}")
            print(f"    Connector value: {conn_val}")
            print(f"    Existing RDF value: {existing_val}")

            if conn_val is not None and str(conn_val).lower() not in ("none", ""):
                print(f"    → Updating {field} with connector value.")
                add_or_replace_literal(dist_node, predicate, conn_val, dtype, is_uri)
            elif existing_val is None:
                print(f"    → Setting {field} explicitly to 'null'.")
                add_or_replace_literal(dist_node, predicate, None, dtype, is_uri)
            else:
                print(f"    → Keeping existing {field} (no connector update).")

        print(f"[DEBUG] Finished normal field updates for {dist_node}")

        # --- Handle checksum (special nested structure) ---
        if "checksum" in field_map:
            checksum_cfg = field_map["checksum"]
            checksum_val = connector_data.get("checksum")
            checksum_nodes = list(graph.objects(dist_node, checksum_cfg["predicate"]))

            print(f"[DEBUG] Handling checksum for {dist_node}")
            print(f"    Connector checksum: {checksum_val}")
            print(f"    Existing checksum nodes: {checksum_nodes}")

            if checksum_val is None or str(checksum_val).lower() in ("none", ""):
                if not checksum_nodes:
                    checksum_uri = URIRef(f"{dist_node}/checksum")
                    graph.add(
                        (
                            checksum_uri,
                            checksum_cfg["nested_predicate"],
                            Literal("null", datatype=checksum_cfg["datatype"]),
                        )
                    )
                    graph.add((dist_node, checksum_cfg["predicate"], checksum_uri))
                    print(f"    → Added 'null' checksum node: {checksum_uri}")
            else:
                checksum_uri = next(
                    iter(checksum_nodes), URIRef(f"{dist_node}/checksum")
                )
                graph.add((dist_node, checksum_cfg["predicate"], checksum_uri))
                graph.add(
                    (
                        checksum_uri,
                        checksum_cfg["nested_predicate"],
                        Literal(checksum_val, datatype=checksum_cfg["datatype"]),
                    )
                )

        print(f"[DEBUG] ✅ Completed connector update for distribution: {dist_node}")

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
