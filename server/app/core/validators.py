from typing import Callable

from abc import ABC, abstractmethod

import yaml
from pyshacl import validate as pyshacl_validate
from rdflib import DCAT
from rdflib import Graph as RDFGraph
from rdflib import URIRef
from rdflib.namespace import RDF, SH

from .entities import Graph
from .exceptions import GraphValidationError
from .namespace import DSPACE

# --- Interfaces ---


class IValidator(ABC):
    @abstractmethod
    def validate(self, entity: Graph) -> None:
        ...


class IValidatorService(ABC):
    validators: list[IValidator]

    @abstractmethod
    def get_validators(self) -> list[IValidator]:
        ...

    @abstractmethod
    def validate(self, entity: Graph) -> None:
        ...


class IDatasetValidatorService(IValidatorService):
    @abstractmethod
    def __init__(
        self,
        shacl_url: str | None = None,
        ontology_url: str | None = None,
        allowed_values_config_path: str | None = None,
    ) -> None:
        ...


# --- Implementations ---


class HasNodeValidator(IValidator):
    def __init__(self, rdf_type: URIRef, single: bool) -> None:
        self.rdf_type = rdf_type
        self.single = single

    def validate(self, entity: Graph) -> None:
        graph = entity.graph
        subjects = list(graph.subjects(RDF.type, self.rdf_type))

        if not subjects:
            raise GraphValidationError(
                "graph_validation_error",
                f"No nodes with type {self.rdf_type} found.",
            )

        if self.single and len(subjects) != 1:
            raise GraphValidationError(
                "graph_validation_error",
                f"Expected exactly one node with type {self.rdf_type}, "
                f"found {len(subjects)}.",
            )


class AllowedValuesValidator(IValidator):
    def __init__(self, config_path: str) -> None:
        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Parse into: {scope: {predicate: {allowed_values}}}
        self.rules: dict[URIRef, dict[URIRef, set[URIRef]]] = {}
        for entry in config["validators"]:
            scope = URIRef(entry["scope"])
            self.rules[scope] = {
                URIRef(rule["predicate"]): {URIRef(v) for v in rule["allowed_values"]}
                for rule in entry["rules"]
            }

    def validate(self, entity: Graph) -> None:
        for scope, predicates in self.rules.items():
            nodes = list(entity.graph.subjects(RDF.type, scope))
            for node in nodes:
                for predicate, allowed in predicates.items():
                    values = list(entity.graph.objects(node, predicate))
                    if not values:
                        raise GraphValidationError(
                            "allowed_values_error",
                            f"Node of type {scope} must have predicate {predicate}.",
                        )
                    allowed_str = ", ".join(sorted(str(v) for v in allowed))
                    for val in values:
                        if val not in allowed:
                            raise GraphValidationError(
                                "allowed_values_error",
                                f"Invalid value {val} for {predicate}. "
                                f"Allowed: {allowed_str}",
                            )


class SHACLValidator(IValidator):
    def __init__(
        self,
        shacl_url: str | None = None,
        ontology_url: str | None = None,
        shacl_validator: Callable[..., tuple[bool, RDFGraph, str]] = pyshacl_validate,
    ) -> None:
        self._shacl_url = shacl_url
        self._ontology_url = ontology_url
        self._shacl_validator = shacl_validator

    def validate(self, entity: Graph) -> None:
        r = self._shacl_validator(
            entity.graph,
            shacl_graph=self._shacl_url,
            ont_graph=self._ontology_url,
            inference="rdfs",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            meta_shacl=False,
            advanced=False,
            js=False,
            debug=False,
        )
        conforms, results_graph, _ = r

        if not conforms:
            errors = []
            for result in results_graph.subjects(RDF.type, SH.ValidationResult):
                error = {}
                for p, o in results_graph.predicate_objects(subject=result):
                    p_ = str(p)
                    pred = p_.split("#")[-1] if "#" in p_ else p_.split("/")[-1]
                    error[pred] = str(o)
                errors.append(error)

            raise GraphValidationError(
                "shacl_validation_error",
                "SHACL validation failed.",
                errors,
            )


class BaseValidatorService(IValidatorService):
    def get_validators(self) -> list[IValidator]:
        if not hasattr(self, "validators") or len(self.validators) == 0:
            raise RuntimeError(
                "No validators configured. Please ensure 'validators' are set."
            )
        return self.validators

    def validate(self, entity: Graph) -> None:
        for validator in self.get_validators():
            validator.validate(entity)


class DatasetValidatorService(BaseValidatorService, IDatasetValidatorService):
    def __init__(
        self,
        shacl_url: str | None = None,
        ontology_url: str | None = None,
        allowed_values_config_path: str | None = None,
    ) -> None:
        if not allowed_values_config_path:
            raise RuntimeError(
                "allowed_values_config_path is required and must not be empty."
            )
        self.validators = [
            HasNodeValidator(rdf_type=DCAT.Dataset, single=True),
            AllowedValuesValidator(allowed_values_config_path),
            SHACLValidator(shacl_url, ontology_url),
        ]


class CatalogFiltersValidatorService(BaseValidatorService):
    validators = [
        HasNodeValidator(rdf_type=DSPACE.Filters, single=True),
    ]
