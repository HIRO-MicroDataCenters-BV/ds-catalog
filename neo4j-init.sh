#!/bin/bash
CYPHER="cypher-shell -a bolt://neo4j:7687 -u neo4j -p 1234567890"

# Wait for Neo4j to be ready
echo "Waiting for Neo4j to be ready..."
until $CYPHER "RETURN 1" > /dev/null 2>&1; do
  sleep 2
done
echo "Neo4j is ready. Initializing n10s..."

# Create required constraint for n10s RDF import (idempotent)
$CYPHER "CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE;" 2>/dev/null || true

# Initialize graph config (idempotent - safe to re-run)
$CYPHER "CALL n10s.graphconfig.init();" 2>/dev/null || true

# Add namespace prefixes (ignore errors if already exist)
$CYPHER 'CALL n10s.nsprefixes.add("dcat", "http://www.w3.org/ns/dcat#");' 2>/dev/null || true
$CYPHER 'CALL n10s.nsprefixes.add("dcterms", "http://purl.org/dc/terms/");' 2>/dev/null || true
$CYPHER 'CALL n10s.nsprefixes.add("dspace", "http://data-space.org/");' 2>/dev/null || true
$CYPHER 'CALL n10s.nsprefixes.add("foaf", "http://xmlns.com/foaf/0.1/");' 2>/dev/null || true
$CYPHER 'CALL n10s.nsprefixes.add("skos", "http://www.w3.org/2004/02/skos/core#");' 2>/dev/null || true
$CYPHER 'CALL n10s.nsprefixes.add("spdx", "http://spdx.org/rdf/terms#");' 2>/dev/null || true
$CYPHER 'CALL n10s.nsprefixes.add("xsd", "http://www.w3.org/2001/XMLSchema#");' 2>/dev/null || true
$CYPHER 'CALL n10s.nsprefixes.add("dcatap", "http://data.europa.eu/r5r/");' 2>/dev/null || true

# Create the initial catalog node (skip if already exists)
echo "Creating initial catalog..."
CATALOG_EXISTS=$($CYPHER "MATCH (c:dcat__Catalog) RETURN count(c) AS cnt;" 2>/dev/null | tail -1)
if [ "$CATALOG_EXISTS" = "0" ]; then
  $CYPHER 'CALL n10s.rdf.import.inline('\''
    {
      "@context": {
        "dcat": "http://www.w3.org/ns/dcat#",
        "dcterms": "http://purl.org/dc/terms/",
        "xsd": "http://www.w3.org/2001/XMLSchema#"
      },
      "@id": "urn:catalog:local",
      "@type": "dcat:Catalog",
      "dcterms:identifier": "local",
      "dcterms:title": "Local Catalog",
      "dcterms:description": "Local development catalog"
    }
  '\'', '\''JSON-LD'\'');'
  echo "Catalog created."
else
  echo "Catalog already exists, skipping."
fi

echo "n10s initialization complete!"
