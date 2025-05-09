from unittest.mock import Mock

import pytest
from rdflib import RDF, SH
from rdflib import Graph as RDFGraph
from rdflib import Literal, Namespace

from ..entities import Graph
from ..exceptions import GraphValidationError
from ..validators import BaseValidatorService, HasNodeValidator, SHACLValidator

EX = Namespace("http://example.org/")
RDFType = EX.TestType


class DummyEntity(Graph):
    label = "d"
    rdf_type = RDFType


class TestHasNodeValidator:
    def test_no_nodes_found(self):
        graph = RDFGraph()
        validator = HasNodeValidator(rdf_type=RDFType, root=False, single=False)
        with pytest.raises(GraphValidationError, match="No nodes with type"):
            validator.validate(DummyEntity(graph))

    def test_single_param(self):
        graph = RDFGraph()
        graph.add((EX.subject1, RDF.type, RDFType))
        graph.add((EX.subject2, RDF.type, RDFType))

        entity_with_single_node = DummyEntity.create_empty("test_id")
        entity_with_multiple_nodes = DummyEntity(graph)

        validator = HasNodeValidator(rdf_type=RDFType, root=False, single=False)
        validator.validate(entity_with_multiple_nodes)

        validator = HasNodeValidator(rdf_type=RDFType, root=False, single=True)
        validator.validate(entity_with_single_node)

        validator = HasNodeValidator(rdf_type=RDFType, root=False, single=True)
        with pytest.raises(GraphValidationError, match="Expected exactly one node"):
            validator.validate(entity_with_multiple_nodes)

    def test_root_param(self):
        graph = RDFGraph()
        graph.add((EX.subject1, RDF.type, EX.AnotherType))
        graph.add((EX.subject2, RDF.type, RDFType))
        graph.add((EX.subject1, EX.relation, EX.subject2))

        entity_with_root_node = DummyEntity.create_empty("test_id")
        entity_with_non_root_nodes = DummyEntity(graph)

        validator = HasNodeValidator(rdf_type=RDFType, root=True, single=False)
        validator.validate(entity_with_root_node)

        validator = HasNodeValidator(rdf_type=RDFType, root=False, single=False)
        validator.validate(entity_with_non_root_nodes)

        validator = HasNodeValidator(rdf_type=RDFType, root=True, single=False)
        with pytest.raises(GraphValidationError, match="No root node with type"):
            validator.validate(entity_with_non_root_nodes)


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
