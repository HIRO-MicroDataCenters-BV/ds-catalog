from unittest.mock import ANY, AsyncMock, Mock

import pytest
from rdflib import Graph as RDFGraph
from rdflib import Literal, URIRef

from ..neosemantics import Neosemantics


class TestNeosemantics:
    @pytest.fixture
    def db_driver(self):
        return Mock()

    @pytest.mark.asyncio
    async def test_export(self, db_driver):
        db_driver.execute_query = AsyncMock(
            return_value=(
                [
                    {
                        "object": "http://example.org/object1",
                        "subject": "http://example.org/subject1",
                        "predicate": "http://example.org/predicate1",
                        "isLiteral": False,
                        "literalLang": None,
                        "literalType": None,
                    },
                    {
                        "object": "Literal value",
                        "subject": "http://example.org/subject2",
                        "predicate": "http://example.org/predicate2",
                        "isLiteral": True,
                        "literalLang": "en",
                        "literalType": None,
                    },
                    {
                        "object": "42",
                        "subject": "http://example.org/subject3",
                        "predicate": "http://example.org/predicate3",
                        "isLiteral": True,
                        "literalLang": None,
                        "literalType": "http://www.w3.org/2001/XMLSchema#integer",
                    },
                ],
                None,
            )
        )

        neosemantics = Neosemantics(db_driver)
        query = "MATCH (n:Node) RETURN n;"
        result = await neosemantics.export(query)

        db_driver.execute_query.assert_called_once_with(
            """
            CALL n10s.rdf.export.cypher(
                $query,
                {stream: True, format: 'RDF'}
            )
            """,
            query=query,
        )

        assert len(result) == 3
        assert (
            URIRef("http://example.org/subject1"),
            URIRef("http://example.org/predicate1"),
            URIRef("http://example.org/object1"),
        ) in result
        assert (
            URIRef("http://example.org/subject2"),
            URIRef("http://example.org/predicate2"),
            Literal("Literal value", lang="en"),
        ) in result
        assert (
            URIRef("http://example.org/subject3"),
            URIRef("http://example.org/predicate3"),
            Literal("42", datatype=URIRef("http://www.w3.org/2001/XMLSchema#integer")),
        ) in result

    @pytest.mark.asyncio
    async def test_save(self, db_driver):
        db_driver.execute_query = AsyncMock(
            return_value={
                "terminationStatus": "OK",
                "extraInfo": "Some info",
            }
        )
        neosemantics = Neosemantics(db_driver)
        graph = RDFGraph()
        graph.add(
            (
                URIRef("http://example.org/subject1"),
                URIRef("http://example.org/predicate1"),
                URIRef("http://example.org/object1"),
            )
        )
        graph.add(
            (
                URIRef("http://example.org/subject2"),
                URIRef("http://example.org/predicate2"),
                Literal("Literal value", lang="en"),
            )
        )

        result = await neosemantics.save(graph)

        db_driver.execute_query.assert_called_once_with(
            "CALL n10s.rdf.import.inline($data, 'JSON-LD');",
            data=graph.serialize(format="json-ld", auto_compact=True),
            result_transformer_=ANY,
        )

        assert result["success"] is True
        assert result["extra_info"] == "Some info"

    @pytest.mark.asyncio
    async def test_save_error(self, db_driver):
        db_driver.execute_query = AsyncMock(
            return_value={
                "terminationStatus": "KO",
                "extraInfo": "Error details",
            }
        )
        neosemantics = Neosemantics(db_driver)
        graph = RDFGraph()
        graph.add(
            (
                URIRef("http://example.org/subject1"),
                URIRef("http://example.org/predicate1"),
                URIRef("http://example.org/object1"),
            )
        )

        result = await neosemantics.save(graph)

        assert result["success"] is False
        assert result["extra_info"] == "Error details"
