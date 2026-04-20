#!/bin/bash
# Require NEO4J_AUTH to be set explicitly (format: username/password).
# Neo4j 5.x enforces a minimum password length, so defaulting to "neo4j/neo4j"
# would silently fail; callers must provide a valid credential pair.
if [ -z "${NEO4J_AUTH:-}" ]; then
  echo "Error: NEO4J_AUTH must be set in the format username/password." >&2
  exit 1
fi
IFS='/' read -r NEO4J_USER NEO4J_PASS <<< "$NEO4J_AUTH"
if [ -z "$NEO4J_USER" ] || [ -z "$NEO4J_PASS" ]; then
  echo "Error: NEO4J_AUTH must be set in the format username/password." >&2
  exit 1
fi

# Use an array to avoid eval and safely handle credentials
CYPHER=(cypher-shell -a bolt://neo4j:7687 -u "$NEO4J_USER" -p "$NEO4J_PASS")

# Wait for Neo4j to be ready (max 5 minutes)
echo "Waiting for Neo4j to be ready..."
MAX_WAIT_SECONDS=${NEO4J_MAX_WAIT_SECONDS:-300}
WAIT_INTERVAL=2
ELAPSED=0
until "${CYPHER[@]}" "RETURN 1" > /dev/null 2>&1; do
  if [ "$ELAPSED" -ge "$MAX_WAIT_SECONDS" ]; then
    echo "Error: Neo4j did not become ready within ${MAX_WAIT_SECONDS} seconds." >&2
    exit 1
  fi
  sleep "$WAIT_INTERVAL"
  ELAPSED=$((ELAPSED + WAIT_INTERVAL))
done
echo "Neo4j is ready. Initializing n10s..."

# Create required constraint for n10s RDF import (idempotent)
"${CYPHER[@]}" "CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE;" 2>/dev/null || true

# Initialize graph config (idempotent - safe to re-run)
"${CYPHER[@]}" "CALL n10s.graphconfig.init();" 2>/dev/null || true

# Add namespace prefixes (ignore errors if already exist)
"${CYPHER[@]}" 'CALL n10s.nsprefixes.add("dcat", "http://www.w3.org/ns/dcat#");' 2>/dev/null || true
"${CYPHER[@]}" 'CALL n10s.nsprefixes.add("dcterms", "http://purl.org/dc/terms/");' 2>/dev/null || true
"${CYPHER[@]}" 'CALL n10s.nsprefixes.add("dspace", "http://data-space.org/");' 2>/dev/null || true
"${CYPHER[@]}" 'CALL n10s.nsprefixes.add("foaf", "http://xmlns.com/foaf/0.1/");' 2>/dev/null || true
"${CYPHER[@]}" 'CALL n10s.nsprefixes.add("skos", "http://www.w3.org/2004/02/skos/core#");' 2>/dev/null || true
"${CYPHER[@]}" 'CALL n10s.nsprefixes.add("spdx", "http://spdx.org/rdf/terms#");' 2>/dev/null || true
"${CYPHER[@]}" 'CALL n10s.nsprefixes.add("xsd", "http://www.w3.org/2001/XMLSchema#");' 2>/dev/null || true
"${CYPHER[@]}" 'CALL n10s.nsprefixes.add("dcatap", "http://data.europa.eu/r5r/");' 2>/dev/null || true

# Create the initial catalog node (skip if already exists)
echo "Creating initial catalog..."
CATALOG_EXISTS=$("${CYPHER[@]}" --format plain "MATCH (c:dcat__Catalog) RETURN count(c) AS cnt;" 2>/dev/null | tail -1)
if [ "$CATALOG_EXISTS" = "0" ]; then
  "${CYPHER[@]}" <<'EOF'
CALL n10s.rdf.import.inline('
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
', 'JSON-LD');
EOF
  echo "Catalog created."
else
  echo "Catalog already exists, skipping."
fi

echo "n10s initialization complete!"
