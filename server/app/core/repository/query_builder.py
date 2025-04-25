from typing import Any, Callable, Self

import json
import re
from collections import defaultdict
from dataclasses import dataclass

from rdflib import DCAT, RDF, BNode
from rdflib import Graph as RDFGraph
from rdflib import Literal, Node, URIRef
from rdflib.namespace import Namespace, NamespaceManager

from app.core.namespace import DSPACE

from ..entities import Catalog, CatalogFilters, Dataset
from ..exceptions import ErrorConstructingQuery
from .queries import FilterCatalog, Query

Triplet = tuple[Node | None, Node | None, Node | None]


def build_cypher_qname(prefix: str, name: str) -> str:
    if prefix == "":
        return name
    else:
        return "__".join((prefix, name))


def uri_to_cypher(uri: str, namespaces: dict[str, str]) -> str:
    """
    Converts a full URI to a Cypher-compatible QName using provided namespace prefixes.

    Example:
        uri_to_cypher(
            "http://www.w3.org/ns/dcat#Dataset", {"dcat": "http://www.w3.org/ns/dcat#"})
        # Output: 'dcat__Dataset'

    """

    g = RDFGraph()
    namespace_manager = NamespaceManager(g)

    for prefix, ns in namespaces.items():
        namespace_manager.bind(prefix, Namespace(ns))

    try:
        prefix, _, name = namespace_manager.compute_qname(URIRef(uri), generate=False)
    except KeyError:
        raise ErrorConstructingQuery(f"No known prefix for {uri}")

    return build_cypher_qname(prefix, name)


def escape_value(value: Any) -> str:
    """
    Escapes a Python value for safe inclusion in a Cypher query using JSON encoding.

    Example:
        escape_value("O'Reilly")    # Output: '"O\'Reilly"'
        escape_value(42)            # Output: '42'
        escape_value(True)          # Output: 'true'
        escape_value(None)          # Output: 'null'

    """

    return json.dumps(value)


def render_cypher_template(template: str, params: dict[str, Any]) -> str:
    """
    Renders a Cypher query template by replacing $placeholders with escaped
    parameter values.

    Example:
        render_cypher_template(
            "MATCH (n:$label) WHERE n.id = $id", {"label": "Person", "id": 123})
        # Output: 'MATCH (n:Person) WHERE n.id = 123'
    """

    def replacer(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in params:
            raise ValueError(f"Missing parameter: {key}")
        return escape_value(params[key])

    return re.sub(r"\$(\w+)", replacer, template)


class LabelGenerator:
    """
    Generates unique labels with a given prefix, optionally using a key to cache
    and reuse results.

    Each prefix maintains its own independent counter. Repeated calls with
    the same key and prefix will return the same label. Presets can be provided
    on initialization.

    Example:
        gen = LabelGenerator()
        gen.generate("n")            # "n1"
        gen.generate("n")            # "n2"
        gen.generate("n", key="a")   # "n3"
        gen.generate("n", key="a")   # "n3" (cached)
        gen.generate("r")            # "r1"
        gen.generate("r")            # "r2"
    """

    def __init__(self, presets: dict[str, dict[Any, str]] | None = None):
        self._counters: defaultdict[str, int] = defaultdict(int)
        self._generated: defaultdict[str, dict[Any, str]] = defaultdict(dict)

        if presets:
            for prefix, keys in presets.items():
                self._generated[prefix].update(keys)

    def generate(self, prefix: str, key: Any | None = None) -> str:
        if key:
            if key in self._generated[prefix]:
                return self._generated[prefix][key]

        self._counters[prefix] += 1
        n = self._counters[prefix]
        result = f"{prefix}{n}"

        if key:
            self._generated[prefix][key] = result

        return result


@dataclass
class FilterTree:
    type: Node | None
    children: dict[Node, list[Self]]
    values: dict[Node, list[Any]]

    def __str__(self) -> str:
        return self.prettify()

    def prettify(self, indent: int = 1) -> str:
        result = ""

        prefix = "  " * indent
        result += f"{prefix}Type: {self.type}\n"

        if self.values:
            result += f"{prefix}  Values:\n"
            for rel, vals in self.values.items():
                result += f"{prefix}    {rel}: {vals}\n"

        if self.children:
            result += f"{prefix}  Children:\n"
            for rel, child_list in self.children.items():
                result += f"{prefix}    Relation: {rel}\n"
                for child in child_list:
                    result += child.prettify(indent + 3)

        return result

    def has_type(self, type_: URIRef) -> bool:
        if self.type == type_:
            return True
        for child_list in self.children.values():
            for c in child_list:
                if c.type == type_ or c.has_type(type_):
                    return True
        return False

    def inference_types(
        self,
        rules: list[Callable[[Node | None, Node | None, Node | None], Triplet]],
    ) -> None:
        if self.type is None:
            for rel, child_list in self.children.items():
                for child in child_list:
                    for rule in rules:
                        s, _, o = rule(self.type, rel, child.type)
                        if s and s != self.type:
                            self.type = s
                        if o and o != child.type:
                            child.type = o


@dataclass
class FilterValue:
    language: str | None
    value: Any


def traverse_graph(
    graph: RDFGraph,
    node: Node,
    visited: set[Node] | None = None,
) -> FilterTree | None:
    """Recursively traverses the RDF graph to build a filters tree"""

    if visited is None:
        visited = set()

    if node in visited:
        return None

    visited.add(node)

    children: dict[Node, list[FilterTree]] = defaultdict(list)
    values: dict[Node, list[Any]] = defaultdict(list)

    for pred, obj in graph.predicate_objects(subject=node):
        if pred == RDF.type:
            continue

        if isinstance(obj, (URIRef, BNode)):
            r = traverse_graph(graph, obj, visited)
            if r is not None:
                children[pred].append(r)
        elif isinstance(obj, Literal):
            value = FilterValue(language=obj.language, value=obj.toPython())
            values[pred].append(value)

    subj_type = graph.value(subject=node, predicate=RDF.type)
    return FilterTree(type=subj_type, children=children, values=values)


class FilterQueryBuilder:
    """Builds a Cypher query from a FilterTree"""

    def __init__(
        self,
        filter_tree: FilterTree,
        namespaces: dict[str, str],
        gen: LabelGenerator | None = None,
    ) -> None:
        if filter_tree.type is None:
            raise ErrorConstructingQuery("Required subject type not specified")

        self.filter_tree = filter_tree
        self.namespaces = namespaces
        self.gen = gen or self._default_label_generator()
        self.query = Query()

    def build(self) -> Query:
        return self._build(1)

    def _build(self, depth: int) -> Query:
        self._add_optional_matches(self.filter_tree, depth)
        self._add_where_statements(self.filter_tree)
        return self.query

    def _default_label_generator(self) -> LabelGenerator:
        return LabelGenerator(
            presets={
                "n": {
                    DCAT.Catalog: Catalog.label,
                    DCAT.Dataset: Dataset.label,
                }
            }
        )

    def _add_optional_matches(self, filter_tree: FilterTree, depth: int) -> None:
        if depth == 1 and not filter_tree.children:
            s_label = self.gen.generate("n", filter_tree.type)
            s_type = f":{uri_to_cypher(str(filter_tree.type), self.namespaces)}"
            self.query.add_optional_match(f"({s_label}{s_type})")
            return

        for rel, children in filter_tree.children.items():
            for child in children:
                if child.type is None:
                    raise ErrorConstructingQuery(
                        f"Required object type not specified for subject "
                        f"{filter_tree.type} and predicate {rel}"
                    )

                s_label = self.gen.generate("n", filter_tree.type)
                p_label = self.gen.generate("r")
                o_label = self.gen.generate("n", child.type)

                s_type = f":{uri_to_cypher(str(filter_tree.type), self.namespaces)}"
                p_type = f":{uri_to_cypher(str(rel), self.namespaces)}"
                o_type = f":{uri_to_cypher(str(child.type), self.namespaces)}"

                self.query.add_optional_match(
                    f"({s_label}{s_type})-[{p_label}{p_type}]->({o_label}{o_type})"
                )

                sub_builder = FilterQueryBuilder(
                    filter_tree=child,
                    namespaces=self.namespaces,
                    gen=self.gen,
                )
                self.query += sub_builder._build(depth + 1)

    def _add_where_statements(self, filter_tree: FilterTree) -> None:
        for rel, values in filter_tree.values.items():
            s_label = self.gen.generate("n", filter_tree.type)
            p_type = uri_to_cypher(str(rel), self.namespaces)
            conditions = [self._build_condition(s_label, p_type, o) for o in values]

            if conditions:
                if len(conditions) == 1:
                    self.query.add_where(conditions[0])
                else:
                    self.query.add_where(f"({' OR '.join(conditions)})")

    def _build_condition(self, s_label: str, p_type: str, o: FilterValue) -> str:
        value_key = self.gen.generate("v")

        if o.language:
            lang_key = self.gen.generate("v")
            return render_cypher_template(
                f"any(t IN {s_label}.{p_type} "
                f"WHERE n10s.rdf.getLangTag(t) = ${lang_key} "
                f"AND n10s.rdf.getValue(t) = ${value_key})",
                params={lang_key: o.language, value_key: o.value},
            )
        else:
            return render_cypher_template(
                f"{s_label}.{p_type} = ${value_key}",
                params={value_key: o.value},
            )


def infer_dcat_dataset_types(
    s: Node | None,
    p: Node | None,
    o: Node | None,
) -> Triplet:
    """Infers subject/object types for the dcat:dataset predicate"""
    if (s is None or o is None) and p == DCAT.dataset:
        return DCAT.Catalog, p, DCAT.Dataset
    return s, p, o


def infer_dspace_extra_metadata_types(
    s: Node | None,
    p: Node | None,
    o: Node | None,
) -> Triplet:
    """Infers subject type for the dspace:extraMetadata predicate"""
    if s is None and p == DSPACE.extraMetadata:
        return DCAT.Dataset, p, o
    return s, p, o


def catalog_filter_to_query(
    filter: CatalogFilters,
    namespaces: dict[str, str],
) -> FilterCatalog:
    """Converts a CatalogFilters instance to a Cypher FilterCatalog query"""

    # TODO: Proccess all filter items
    filter_items = list(filter.graph.objects(predicate=DSPACE.filters))
    if not filter_items:
        raise ErrorConstructingQuery("The first filter item was not found")
    if len(filter_items) > 1:
        raise ErrorConstructingQuery("Multiple filter items found")

    first_filter = filter_items[0]

    filter_tree = traverse_graph(filter.graph, first_filter)
    if filter_tree is None:
        raise ErrorConstructingQuery("Failed to process filters")

    filter_tree.inference_types(
        rules=[
            infer_dcat_dataset_types,
            infer_dspace_extra_metadata_types,
        ]
    )

    query = FilterQueryBuilder(filter_tree, namespaces).build()

    has_root_type = filter_tree.has_type(DCAT.Dataset)
    if not has_root_type:
        query.add_optional_match(
            f"({Dataset.label}:{uri_to_cypher(DCAT.Dataset, namespaces)})"
        )

    query.with_clause = Dataset.label

    return FilterCatalog() + query
