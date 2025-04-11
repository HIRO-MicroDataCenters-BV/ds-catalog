import rdflib

from app.database import DatabaseDriver


class Neosemantics:
    def __init__(self, db_driver: DatabaseDriver) -> None:
        self._db_driver = db_driver

    async def export(self, query: str) -> rdflib.Graph:
        result, *other = await self._db_driver.execute_query(
            """
            CALL n10s.rdf.export.cypher(
                $query,
                {stream: True, format: 'RDF'}
            )
            """,
            query=query,
        )

        graph = rdflib.Graph()

        for item in result:
            object_ = item["object"]
            subject = rdflib.URIRef(item["subject"])
            predicate = rdflib.URIRef(item["predicate"])

            is_literal = item["isLiteral"]
            literal_lang = item["literalLang"]
            literal_type = item["literalType"]

            if is_literal:
                if literal_lang:
                    object_ = rdflib.Literal(object_, lang=literal_lang)
                elif literal_type:
                    object_ = rdflib.Literal(object_, datatype=literal_type)
                else:
                    object_ = rdflib.Literal(object_)
            else:
                object_ = rdflib.URIRef(object_)

            graph.add((subject, predicate, object_))

        return graph

    async def save(self, graph: rdflib.Graph) -> dict[str, int]:
        data_str = graph.serialize(format="json-ld", auto_compact=True)
        result = await self._db_driver.execute_query(
            "CALL n10s.rdf.import.inline($data, 'JSON-LD');",
            data=data_str,
            result_transformer_=lambda r: r.single(strict=True),
        )
        return {
            "success": result["terminationStatus"] == "OK",
            "extra_info": result.get("extraInfo", None),
        }
