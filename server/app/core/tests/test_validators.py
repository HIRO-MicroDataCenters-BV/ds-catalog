from unittest.mock import Mock

import pytest
from rdflib import RDF, SH
from rdflib import Graph as RDFGraph
from rdflib import Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS

from ..entities import Graph
from ..exceptions import GraphValidationError
from ..validators import (
    BaseValidatorService,
    CatalogItemTypeValidator,
    HasNodeValidator,
    SHACLValidator,
)

EX = Namespace("http://example.org/")
RDFType = EX.TestType

DATASET_TYPE = "http://purl.org/dc/dcmitype/Dataset"
SOFTWARE_TYPE = "http://purl.org/dc/dcmitype/Software"


class DummyEntity(Graph):
    label = "d"
    rdf_type = RDFType


class TestHasNodeValidator:
    def test_no_nodes_found(self):
        graph = RDFGraph()
        validator = HasNodeValidator(rdf_type=RDFType, single=False)
        with pytest.raises(GraphValidationError, match="No nodes with type"):
            validator.validate(DummyEntity(graph))

    def test_single_param(self):
        graph = RDFGraph()
        graph.add((EX.subject1, RDF.type, RDFType))
        graph.add((EX.subject2, RDF.type, RDFType))

        entity_with_single_node = DummyEntity.create_empty("test_id")
        entity_with_multiple_nodes = DummyEntity(graph)

        validator = HasNodeValidator(rdf_type=RDFType, single=False)
        validator.validate(entity_with_multiple_nodes)

        validator = HasNodeValidator(rdf_type=RDFType, single=True)
        validator.validate(entity_with_single_node)

        validator = HasNodeValidator(rdf_type=RDFType, single=True)
        with pytest.raises(GraphValidationError, match="Expected exactly one node"):
            validator.validate(entity_with_multiple_nodes)


class TestSHACLValidator:
    def test_valid_graph(self):
        entity = DummyEntity.create_empty("test_id")

        shacl_url = "http://example.org/shacl.ttl"
        ontology_url = "http://example.org/ont.ttl"

        shacl_validator = Mock(return_value=(True, RDFGraph(), ""))

        validator = SHACLValidator(
            shacl_url=shacl_url,
            ontology_url=ontology_url,
            shacl_validator=shacl_validator,
        )

        validator.validate(entity)

        shacl_validator.assert_called_once()
        args, kwargs = shacl_validator.call_args
        assert len(args) == 1
        assert args[0] == entity.graph
        assert kwargs["shacl_graph"] == shacl_url
        assert kwargs["ont_graph"] == ontology_url

    def test_invalid_graph_raises_error(self):
        entity = DummyEntity.create_empty("test_id")

        results_graph = RDFGraph()
        result_node = EX.result1
        results_graph.add((result_node, RDF.type, SH.ValidationResult))
        results_graph.add((result_node, SH.resultMessage, Literal("Invalid data")))
        results_graph.add((result_node, SH.focusNode, EX.subject))

        shacl_validator = Mock(return_value=(False, results_graph, "some error"))

        validator = SHACLValidator(
            shacl_url=None,
            ontology_url=None,
            shacl_validator=shacl_validator,
        )

        with pytest.raises(GraphValidationError) as exc_info:
            validator.validate(entity)

        assert exc_info.value.code == "shacl_validation_error"
        assert exc_info.value.message == "SHACL validation failed."
        assert isinstance(exc_info.value.details, list)
        assert exc_info.value.details == [
            {
                "type": str(SH.ValidationResult),
                "resultMessage": "Invalid data",
                "focusNode": str(EX.subject),
            }
        ]


class TestBaseValidatorService:
    def test_get_validators_missing_attribute(self):
        class ServiceWithoutValidators(BaseValidatorService):
            pass

        service = ServiceWithoutValidators()
        with pytest.raises(RuntimeError, match="No validators configured"):
            service.get_validators()

    def test_get_empty_list_of_validators(self):
        class ServiceWithNoneValidators(BaseValidatorService):
            validators = []

        service = ServiceWithNoneValidators()
        with pytest.raises(RuntimeError, match="No validators configured"):
            service.get_validators()

    def test_validate_calls_all_validators(self):
        validator1 = Mock()
        validator2 = Mock()

        class ValidatingService(BaseValidatorService):
            validators = [validator1, validator2]

        service = ValidatingService()
        entity = DummyEntity()

        service.validate(entity)

        validator1.validate.assert_called_once_with(entity)
        validator2.validate.assert_called_once_with(entity)


class DatasetEntity(Graph):
    label = "d"
    rdf_type = DCAT.Dataset


class TestCatalogItemTypeValidator:
    def _make_dataset_with_type(self, type_uri: str) -> DatasetEntity:
        graph = RDFGraph()
        node = EX.dataset1
        graph.add((node, RDF.type, DCAT.Dataset))
        graph.add((node, DCTERMS.type, URIRef(type_uri)))
        return DatasetEntity(graph)

    def _make_dataset_without_type(self) -> DatasetEntity:
        graph = RDFGraph()
        node = EX.dataset1
        graph.add((node, RDF.type, DCAT.Dataset))
        return DatasetEntity(graph)

    def test_valid_dataset_type(self):
        entity = self._make_dataset_with_type(DATASET_TYPE)
        validator = CatalogItemTypeValidator([DATASET_TYPE, SOFTWARE_TYPE])
        validator.validate(entity)

    def test_valid_software_type(self):
        entity = self._make_dataset_with_type(SOFTWARE_TYPE)
        validator = CatalogItemTypeValidator([DATASET_TYPE, SOFTWARE_TYPE])
        validator.validate(entity)

    def test_missing_type_raises_error(self):
        entity = self._make_dataset_without_type()
        validator = CatalogItemTypeValidator([DATASET_TYPE, SOFTWARE_TYPE])
        with pytest.raises(GraphValidationError, match="must have a dcterms:type"):
            validator.validate(entity)

    def test_invalid_type_raises_error(self):
        entity = self._make_dataset_with_type("http://example.org/InvalidType")
        validator = CatalogItemTypeValidator([DATASET_TYPE, SOFTWARE_TYPE])
        with pytest.raises(GraphValidationError, match="Invalid catalog item type"):
            validator.validate(entity)

    def test_empty_allowed_types_rejects_all(self):
        entity = self._make_dataset_with_type(DATASET_TYPE)
        validator = CatalogItemTypeValidator([])
        with pytest.raises(GraphValidationError, match="Invalid catalog item type"):
            validator.validate(entity)

    def test_no_dataset_nodes_passes(self):
        """If there are no dcat:Dataset nodes, validation passes (nothing to check)."""
        graph = RDFGraph()
        graph.add((EX.something, RDF.type, EX.OtherType))
        entity = DatasetEntity(graph)
        validator = CatalogItemTypeValidator([DATASET_TYPE])
        validator.validate(entity)
