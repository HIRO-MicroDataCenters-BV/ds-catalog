import pytest
from rdflib import DCAT, DCTERMS, RDF
from rdflib import Graph as RDFGraph
from rdflib import Literal, URIRef

from app.core.exceptions import ErrorConstructingQuery
from app.core.namespace import DSPACE
from app.core.tests.factories import catalog_filters_factory

from ..query_builder import (
    FilterQueryBuilder,
    FilterTree,
    FilterValue,
    LabelGenerator,
    build_cypher_qname,
    catalog_filter_to_query,
    escape_value,
    infer_dcat_dataset_types,
    infer_dspace_extra_metadata_types,
    render_cypher_template,
    traverse_graph,
    uri_to_cypher,
)


@pytest.mark.parametrize(
    "prefix, name, expected",
    [
        ("", "label", "label"),
        ("ns", "label", "ns__label"),
        ("data", "123", "data__123"),
        ("prefix", "", "prefix__"),
        ("", "", ""),
    ],
)
def test_build_cypher_qname(prefix, name, expected):
    result = build_cypher_qname(prefix, name)
    assert result == expected


class TestUriToCypher:
    def test_success(self):
        uri = "http://www.w3.org/ns/dcat#Dataset"
        namespaces = {"dcat": "http://www.w3.org/ns/dcat#"}
        result = uri_to_cypher(uri, namespaces)
        assert result == "dcat__Dataset"

    def test_missing_prefix(self):
        uri = "http://unknown.org/Entity"
        namespaces = {"dcat": "http://www.w3.org/ns/dcat#"}
        with pytest.raises(ErrorConstructingQuery) as exc_info:
            uri_to_cypher(uri, namespaces)
        assert "No known prefix for" in str(exc_info.value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("O'Reilly", '"O\'Reilly"'),
        ('He said "Hi"', '"He said \\"Hi\\""'),
        (42, "42"),
        (3.14, "3.14"),
        (True, "true"),
        (False, "false"),
        (None, "null"),
    ],
)
def test_escape_value(value, expected):
    assert escape_value(value) == expected


class TestRenderCypherTemplate:
    def test_common(self):
        template = "MATCH (n:$label) WHERE n.id = $id"
        params = {"label": "Person", "id": 123}
        expected = 'MATCH (n:"Person") WHERE n.id = 123'
        assert render_cypher_template(template, params) == expected

    def test_string_escaping(self):
        template = "CREATE (n:User {name: $name})"
        params = {"name": "O'Reilly"}
        expected = 'CREATE (n:User {name: "O\'Reilly"})'
        assert render_cypher_template(template, params) == expected

    def test_boolean_and_null(self):
        template = "MATCH (n) WHERE n.active = $active AND n.deleted IS $deleted"
        params = {"active": True, "deleted": None}
        expected = "MATCH (n) WHERE n.active = true AND n.deleted IS null"
        assert render_cypher_template(template, params) == expected

    def test_missing_param(self):
        template = "MATCH (n) WHERE n.id = $id"
        with pytest.raises(ValueError, match="Missing parameter: id"):
            render_cypher_template(template, {})

    def test_multiple_occurrences(self):
        template = "MATCH (n:$label)-[:KNOWS]->(m:$label) RETURN n, m"
        params = {"label": "Person"}
        expected = 'MATCH (n:"Person")-[:KNOWS]->(m:"Person") RETURN n, m'
        assert render_cypher_template(template, params) == expected


class TestLabelGenerator:
    def test_common(self):
        gen = LabelGenerator()
        assert gen.generate("n") == "n1"
        assert gen.generate("n") == "n2"

    def test_with_key(self):
        gen = LabelGenerator()
        assert gen.generate("n", key="a") == "n1"
        assert gen.generate("n", key="a") == "n1"
        assert gen.generate("n", key="b") == "n2"

    def test_presets(self):
        presets = {"n": {"a": "x", "b": "y"}, "r": {"c": "z"}}
        gen = LabelGenerator(presets=presets)

        assert gen.generate("n", key="a") == "x"
        assert gen.generate("n", key="b") == "y"
        assert gen.generate("r", key="c") == "z"

        assert gen.generate("n", key="d") == "n1"
        assert gen.generate("n") == "n2"
        assert gen.generate("n", key="d") == "n1"

        assert gen.generate("r") == "r1"
        assert gen.generate("r") == "r2"

    def test_no_key(self):
        gen = LabelGenerator()
        assert gen.generate("n") == "n1"
        assert gen.generate("n") == "n2"
        assert gen.generate("r") == "r1"

    def test_multiple_prefixes(self):
        gen = LabelGenerator()
        assert gen.generate("n") == "n1"
        assert gen.generate("r") == "r1"
        assert gen.generate("n") == "n2"
        assert gen.generate("r") == "r2"


class TestFilterTree:
    @pytest.fixture
    def tree(self):
        return FilterTree(
            type=URIRef("http://example.org/Person"),
            children={
                URIRef("http://example.org/hasChild"): [
                    FilterTree(
                        type=URIRef("http://example.org/Child"),
                        children={},
                        values={},
                    ),
                ],
            },
            values={URIRef("http://example.org/name"): ["John"]},
        )

    def test_pretty_print(self, snapshot_for_class, tree):
        result = tree.prettify()
        snapshot_for_class.assert_match(result, "snapshot")

    def test_has_type(self, tree):
        assert tree.has_type(URIRef("http://example.org/Child")) is True
        assert tree.has_type(URIRef("http://example.org/Person")) is True
        assert tree.has_type(URIRef("http://example.org/Unknown")) is False

    def test_inference_types(self):
        def sample_rule(s, p, o):
            if p == URIRef("http://example.org/hasChild"):
                return [
                    URIRef("http://example.org/Person"),
                    p,
                    URIRef("http://example.org/Child"),
                ]
            return s, p, o

        tree = FilterTree(
            type=None,
            children={
                URIRef("http://example.org/hasChild"): [
                    FilterTree(type=None, children={}, values={}),
                ],
            },
            values={},
        )

        tree.inference_types([sample_rule])

        assert tree.type == URIRef("http://example.org/Person")
        assert tree.children[URIRef("http://example.org/hasChild")][0].type == URIRef(
            "http://example.org/Child"
        )


class TestTraverseGraph:
    @pytest.fixture
    def example_graph(self):
        g = RDFGraph()

        person_uri = URIRef("http://example.org/Person1")
        child_uri = URIRef("http://example.org/Child1")

        g.add((person_uri, RDF.type, URIRef("http://example.org/Person")))
        g.add((person_uri, URIRef("http://example.org/hasChild"), child_uri))
        g.add((child_uri, RDF.type, URIRef("http://example.org/Child")))
        g.add((child_uri, URIRef("http://example.org/hasName"), Literal("John Doe")))

        return g

    def test_common(self, example_graph):
        node = URIRef("http://example.org/Person1")
        result = traverse_graph(example_graph, node)

        assert result is not None
        assert result.type == URIRef("http://example.org/Person")
        assert result.values == {}
        assert result.children
        assert URIRef("http://example.org/hasChild") in result.children
        assert len(result.children[URIRef("http://example.org/hasChild")]) == 1
        child = result.children[URIRef("http://example.org/hasChild")][0]
        assert not child.children
        assert child.values == {
            URIRef("http://example.org/hasName"): [
                FilterValue(language=None, value="John Doe"),
            ],
        }

    def test_empty_graph(self):
        g = RDFGraph()
        node = URIRef("http://example.org/Person1")

        result = traverse_graph(g, node)

        assert result is not None
        assert result.type is None
        assert result.values == {}
        assert result.children == {}


class TestFilterQueryBuilder:
    @pytest.fixture
    def namespaces(self):
        return {
            "dcat": "http://www.w3.org/ns/dcat#",
            "dcterms": "http://purl.org/dc/terms/",
            "dspace": "http://data-space.org/",
            "med": "http://med.example.org/",
        }

    def test_common(self, snapshot_for_class, namespaces):
        filter_tree = FilterTree(
            type=DCAT.Catalog,
            values={},
            children={
                DCAT.dataset: [
                    FilterTree(
                        type=DCAT.Dataset,
                        values={
                            DCTERMS.identifier: [
                                FilterValue(value="123", language=None),
                            ],
                            DCTERMS.title: [
                                FilterValue(value="Test Title", language="en"),
                                FilterValue(value="Titel", language="de"),
                            ],
                        },
                        children={
                            DSPACE.extraMetadata: [
                                FilterTree(
                                    type=URIRef("http://med.example.org/Patient"),
                                    values={
                                        URIRef("http://med.example.org/height"): [
                                            FilterValue(value=180, language=None),
                                        ]
                                    },
                                    children={},
                                )
                            ]
                        },
                    )
                ]
            },
        )

        builder = FilterQueryBuilder(filter_tree, namespaces)
        result = builder.build()

        snapshot_for_class.assert_match(str(result), "snapshot")

    def test_single_node(self, snapshot_for_class, namespaces):
        filter_tree = FilterTree(
            type=DCAT.Dataset,
            children={},
            values={
                DCTERMS.title: [
                    FilterValue(value="Test Title", language=None),
                ]
            },
        )
        builder = FilterQueryBuilder(filter_tree, namespaces)
        result = builder.build()
        snapshot_for_class.assert_match(str(result), "snapshot")

    def test_missing_subject_type_raises(self):
        filter_tree = FilterTree(type=None, children={}, values={})

        with pytest.raises(ErrorConstructingQuery):
            FilterQueryBuilder(filter_tree, namespaces={})

    def test_missing_child_type_raises(self, namespaces):
        filter_tree = FilterTree(
            type=DCAT.Catalog,
            children={DCAT.dataset: [FilterTree(type=None, children={}, values={})]},
            values={},
        )

        with pytest.raises(ErrorConstructingQuery):
            FilterQueryBuilder(filter_tree, namespaces).build()


class TestInferDcatDatasetTypes:
    def test_common(self):
        s, p, o = infer_dcat_dataset_types(None, DCAT.dataset, None)
        assert (s, p, o) == (DCAT.Catalog, DCAT.dataset, DCAT.Dataset)

    def test_p_not_dcat_dataset(self):
        pred, obj = URIRef("pred"), URIRef("obj")
        result = infer_dcat_dataset_types(None, pred, obj)
        assert result == (None, pred, obj)

    def test_s_and_o_are_provided(self):
        subj, obj = URIRef("subj"), URIRef("obj")
        result = infer_dcat_dataset_types(subj, DCAT.dataset, obj)
        assert result == (subj, DCAT.dataset, obj)


class TestInferDspaceExtraMetadataTypes:
    def test_common(self):
        obj = URIRef("obj")
        s, p, o = infer_dspace_extra_metadata_types(None, DSPACE.extraMetadata, obj)
        assert (s, p, o) == (DCAT.Dataset, DSPACE.extraMetadata, obj)

    def test_p_not_extra_metadata(self):
        pred, obj = URIRef("pred"), URIRef("obj")
        result = infer_dspace_extra_metadata_types(None, pred, obj)
        assert result == (None, pred, obj)

    def test_s_provided(self):
        subj, obj = URIRef("subj"), URIRef("obj")
        result = infer_dspace_extra_metadata_types(subj, DSPACE.extraMetadata, obj)
        assert result == (subj, DSPACE.extraMetadata, obj)


class TestCatalogFilterToQuery:
    @pytest.fixture
    def namespaces(self):
        return {
            "dcat": "http://www.w3.org/ns/dcat#",
            "dcterms": "http://purl.org/dc/terms/",
            "dspace": "http://data-space.org/",
            "med": "http://med.example.org/",
        }

    def test_common(self, snapshot_for_class, namespaces):
        filters = catalog_filters_factory(
            filter_items=[{"dcat:dataset": {"dcterms:identifier": "123"}}]
        )
        result = catalog_filter_to_query(filters, namespaces)
        snapshot_for_class.assert_match(str(result), "snapshot")

    def test_without_root_node(self, snapshot_for_class, namespaces):
        filters = catalog_filters_factory(
            filter_items=[
                {
                    "@type": "http://med.example.org/Diagnosis",
                    "http://med.example.org/code": "I10",
                }
            ]
        )
        result = catalog_filter_to_query(filters, namespaces)
        snapshot_for_class.assert_match(str(result), "snapshot")

    def test_when_no_filter_items(self, namespaces):
        filters = catalog_filters_factory(filter_items=[])
        result = catalog_filter_to_query(filters, namespaces)
        assert result is None

    def test_raises_error_when_multiple_filter_items(self, namespaces):
        filters = catalog_filters_factory(filter_items=[{}, {}])
        with pytest.raises(ErrorConstructingQuery, match="Multiple filter items found"):
            catalog_filter_to_query(filters, namespaces)
