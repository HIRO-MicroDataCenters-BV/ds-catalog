"""Permission map used when ds-auth is enabled on ds-catalog.

Design:
  * All GET endpoints (browsing the local or public catalog, fetching a
    dataset / mmio / filters definition) require ``catalog:read``.
  * All POST/DELETE endpoints (saving a dataset, creating mmio, sharing,
    unsharing, deleting) require ``catalog:write``.
  * Health, docs, OpenAPI and Prometheus metrics stay public.

The two POSTs on ``/catalog/`` and ``/public-catalog/`` are *reads* despite
being POST (the body carries the filter spec), so they map to ``catalog:read``.
"""

from __future__ import annotations

READ_PERMISSION = "catalog:read"
WRITE_PERMISSION = "catalog:write"

# (METHOD, path regex, required permission). First match wins.
PERMISSION_MAP: list[tuple[str, str, str]] = [
    # Catalog browse (POSTs that act as reads — body carries the filter spec)
    ("POST", r"^/catalog/?$", READ_PERMISSION),
    ("POST", r"^/public-catalog/?$", READ_PERMISSION),
    ("GET", r"^/catalog/filters/?$", READ_PERMISSION),
    # Datasets
    ("GET", r"^/datasets/[^/]+/?$", READ_PERMISSION),
    ("POST", r"^/datasets/[^/]+/?$", WRITE_PERMISSION),
    ("DELETE", r"^/datasets/[^/]+/?$", WRITE_PERMISSION),
    ("POST", r"^/datasets/[^/]+/share/?$", WRITE_PERMISSION),
    ("POST", r"^/datasets/[^/]+/unshare/?$", WRITE_PERMISSION),
    # MMIO
    ("POST", r"^/mmio/?$", WRITE_PERMISSION),
    ("GET", r"^/mmio/[^/]+/?$", READ_PERMISSION),
    ("DELETE", r"^/mmio/[^/]+/?$", WRITE_PERMISSION),
]


# Paths that bypass auth entirely — operational endpoints and docs.
PUBLIC_PATHS: tuple[str, ...] = (
    "/health-check",
    "/health-check/",
    "/metrics",
    "/openapi.json",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
)
