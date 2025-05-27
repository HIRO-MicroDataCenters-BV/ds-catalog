from app.core.entities import Dataset, Person

from ..queries import FilterDatasetByID, FilterPersonByID, Query


class TestQueries:
    def test_initialization(self):
        query = Query(
            match=["(n:Node)"],
            optional_match=["(n)-[:REL]->(m)"],
            where=["n.name='Test'"],
            with_clause="n, m",
            return_clause=["n", "m"],
            order_by="n.name",
            skip=10,
            limit=5,
        )
        assert query.match == ["(n:Node)"]
        assert query.optional_match == ["(n)-[:REL]->(m)"]
        assert query.where == ["n.name='Test'"]
        assert query.with_clause == "n, m"
        assert query.return_clause == ["n", "m"]
        assert query.order_by == "n.name"
        assert query.skip == 10
        assert query.limit == 5

    def test_add(self):
        query1 = Query(match=["(n:Node)"], where=["n.name='Test'"], return_clause=["n"])
        query2 = Query(optional_match=["(n)-[:REL]->(m)"], return_clause=["m"])
        combined_query = query1 + query2
        assert combined_query.match == ["(n:Node)"]
        assert combined_query.optional_match == ["(n)-[:REL]->(m)"]
        assert combined_query.where == ["n.name='Test'"]
        assert combined_query.return_clause == ["n", "m"]

    def test_str(self):
        query = Query(match=["(n:Node)"])
        query_str = str(query)
        assert query_str == query.build()

    def test_eq(self):
        query1 = Query(match=["(n:Node)"])
        query2 = Query(match=["(n:Node)"])
        query3 = Query(match=["(n:Node)"], return_clause=["n"])
        assert query1 == query2
        assert query1 != query3

    def test_add_methods(self):
        query = Query()
        query.add_match("(n:Node)")
        query.add_optional_match("(n)-[:REL]->(m)")
        query.add_where("n.name='Test 1'")
        query.add_where("m.name='Test 2'")
        query.add_return("n")
        query.add_return("m")
        assert query.match == ["(n:Node)"]
        assert query.optional_match == ["(n)-[:REL]->(m)"]
        assert query.where == ["n.name='Test 1'", "m.name='Test 2'"]
        assert query.return_clause == ["n", "m"]

    def test_build(self):
        query = Query(
            match=["(n:Node)", "(n)-[:REL1]->(m)"],
            optional_match=["(n)-[:REL2]->(x)", "(x)-[:REL3]->(y)"],
            where=["n.name='Test 1'", "m.name='Test 2'"],
            with_clause="n, m",
            return_clause=["n", "m"],
            order_by="n.name",
            skip=10,
            limit=5,
        )
        built_query = query.build()
        expected_query = (
            "MATCH (n:Node), (n)-[:REL1]->(m)\n"
            "OPTIONAL MATCH (n)-[:REL2]->(x), (x)-[:REL3]->(y)\n"
            "WHERE n.name='Test 1' AND m.name='Test 2'\n"
            "WITH n, m\n"
            "RETURN n, m\n"
            "ORDER BY n.name\n"
            "SKIP 10\n"
            "LIMIT 5"
        )
        assert built_query == expected_query

    def test_build_together(self):
        query1 = Query(match=["(n:Node)"], where=["n.name='Test'"])
        query2 = Query(optional_match=["(n)-[:REL]->(m)"], return_clause=["m"])
        combined_query = Query.build_together(query1, query2)
        expected_query = (
            "MATCH (n:Node)\n"
            "WHERE n.name='Test'\n"
            "OPTIONAL MATCH (n)-[:REL]->(m)\n"
            "RETURN m"
        )
        assert combined_query == expected_query


def test_filter_dataset_by_id():
    query = FilterDatasetByID("123")
    assert query.where == [f'{Dataset.label}.dcterms__identifier="123"']


def test_filter_person_by_id():
    query = FilterPersonByID("456")
    assert query.where == [f'{Person.label}.dcterms__identifier="456"']
