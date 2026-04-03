from typing import Callable

from abc import ABC, abstractmethod

import yaml
from pyshacl import validate as pyshacl_validate
from rdflib import DCAT
from rdflib import Graph as RDFGraph
from rdflib import URIRef
from rdflib.namespace import RDF, SH

from .entities import Graph
from .exceptions import ConfigurationError, GraphValidationError
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
        allowed_values_config_path: str,
        shacl_url: str | None = None,
        ontology_url: str | None = None,
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
    # Cache parsed rules per config path to avoid repeated disk I/O per request.
    # Note: cache is process-scoped. Updates to the YAML file take effect only
    # after a process restart (e.g. pod restart in Kubernetes).
    _rules_cache: dict[str, dict[URIRef, dict[URIRef, set[URIRef]]]] = {}

    def __init__(self, config_path: str) -> None:
        self.rules = self._get_or_load_rules(config_path)

    @classmethod
    def _get_or_load_rules(
        cls, config_path: str
    ) -> dict[URIRef, dict[URIRef, set[URIRef]]]:
        cached = cls._rules_cache.get(config_path)
        if cached is not None:
            return cached

        try:
            with open(config_path, encoding="utf-8") as f:
                raw_config = f.read()
        except OSError as exc:
            raise ConfigurationError(
                f"Failed to load allowed values config from '{config_path}': {exc}"
            ) from exc

        try:
            config = yaml.safe_load(raw_config)
        except yaml.YAMLError as exc:
            raise ConfigurationError(
                f"Malformed YAML in allowed values config '{config_path}': {exc}"
            ) from exc

        if not isinstance(config, dict):
            raise ConfigurationError(
                f"Invalid allowed values config in '{config_path}': "
                "expected a mapping at the top level."
            )

        validators = config.get("validators")
        if not isinstance(validators, list):
            raise ConfigurationError(
                f"Invalid allowed values config in '{config_path}': "
                "missing or non-list 'validators' key."
            )

        rules: dict[URIRef, dict[URIRef, set[URIRef]]] = {}
        for idx, entry in enumerate(validators):
            if not isinstance(entry, dict):
                raise ConfigurationError(
                    f"Invalid validator entry at index {idx} in '{config_path}': "
                    "expected a mapping."
                )
            try:
                scope_str = entry["scope"]
                entry_rules = entry["rules"]
            except KeyError as exc:
                raise ConfigurationError(
                    f"Invalid validator entry at index {idx} in '{config_path}': "
                    f"missing key {exc!s}."
                ) from exc

            if not isinstance(scope_str, str):
                raise ConfigurationError(
                    f"Invalid validator entry at index {idx} in '{config_path}': "
                    f"'scope' must be a string, got {type(scope_str).__name__}."
                )

            if not isinstance(entry_rules, list):
                raise ConfigurationError(
                    f"Invalid 'rules' for scope '{scope_str}' in '{config_path}': "
                    "expected a list."
                )

            scope = URIRef(scope_str)
            predicate_rules: dict[URIRef, set[URIRef]] = {}
            for rule_idx, rule in enumerate(entry_rules):
                if not isinstance(rule, dict):
                    raise ConfigurationError(
                        f"Invalid rule at index {rule_idx} for scope '{scope_str}' "
                        f"in '{config_path}': expected a mapping."
                    )
                try:
                    predicate_str = rule["predicate"]
                    allowed_values = rule["allowed_values"]
                except KeyError as exc:
                    raise ConfigurationError(
                        f"Invalid rule at index {rule_idx} for scope '{scope_str}' "
                        f"in '{config_path}': missing key {exc!s}."
                    ) from exc

                if not isinstance(predicate_str, str):
                    raise ConfigurationError(
                        f"Invalid rule at index {rule_idx} for scope '{scope_str}' "
                        f"in '{config_path}': 'predicate' must be a string, "
                        f"got {type(predicate_str).__name__}."
                    )

                if not isinstance(allowed_values, (list, set, tuple)):
                    raise ConfigurationError(
                        f"Invalid 'allowed_values' for predicate '{predicate_str}' "
                        f"in scope '{scope_str}' in '{config_path}': "
                        "expected a list of values."
                    )

                for val_idx, val in enumerate(allowed_values):
                    if not isinstance(val, str):
                        raise ConfigurationError(
                            f"Invalid value at index {val_idx} in 'allowed_values' "
                            f"for predicate '{predicate_str}' in scope '{scope_str}' "
                            f"in '{config_path}': expected a string, "
                            f"got {type(val).__name__}."
                        )

                predicate_rules[URIRef(predicate_str)] = {
                    URIRef(v) for v in allowed_values
                }

            if scope in rules:
                raise ConfigurationError(
                    f"Invalid allowed values config in '{config_path}': "
                    f"duplicate scope '{scope}'. Each scope must be defined only once."
                )
            rules[scope] = predicate_rules

        cls._rules_cache[config_path] = rules
        return rules

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
                    for val in values:
                        if val not in allowed:
                            allowed_str = ", ".join(sorted(str(v) for v in allowed))
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
        allowed_values_config_path: str,
        shacl_url: str | None = None,
        ontology_url: str | None = None,
    ) -> None:
        if not allowed_values_config_path:
            raise ConfigurationError(
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
