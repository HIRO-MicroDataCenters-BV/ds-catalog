from abc import ABC, abstractmethod

from pyshacl import validate as pyshacl_validate
from rdflib import DCAT, URIRef
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
    ) -> None:
        ...


# --- Implementations ---


class HasNodeValidator(IValidator):
    def __init__(self, rdf_type: URIRef, root: bool, single: bool) -> None:
        self.rdf_type = rdf_type
        self.root = root
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

        if self.root:
            for subj in subjects:
                if not any(graph.triples((None, None, subj))):
                    return
            raise GraphValidationError(
                "graph_validation_error",
                f"No root node with type {self.rdf_type} found.",
            )


class SHACLValidator(IValidator):
    def __init__(
        self,
        shacl_url: str | None = None,
        ontology_url: str | None = None,
    ) -> None:
        self.shacl_url = shacl_url
        self.ontology_url = ontology_url

    def validate(self, entity: Graph) -> None:
        r = pyshacl_validate(
            entity.graph,
            shacl_graph=self.shacl_url,
            ont_graph=self.ontology_url,
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
                    pred = p.split("#")[-1] if "#" in p else p.split("/")[-1]
                    error[pred] = str(o)
                errors.append(error)

            raise GraphValidationError(
                "shacl_validation_error",
                "SHACL validation failed.",
                errors,
            )


class BaseValidatorService(IValidatorService):
    def get_validators(self) -> list[IValidator]:
        if not hasattr(self, "validators") or self.validators is None:
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
    ) -> None:
        self.validators = [
            HasNodeValidator(rdf_type=DCAT.Dataset, root=True, single=True),
            SHACLValidator(shacl_url, ontology_url),
        ]


class CatalogFiltersValidatorService(BaseValidatorService):
    validators = [
        HasNodeValidator(rdf_type=DSPACE.Filters, root=True, single=True),
    ]
