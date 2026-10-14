"""Tests for the optional ds-auth integration.

These tests only verify the wiring — that auth is OFF by default, that the
permission map covers the right endpoints, and that enabling it loads the
middleware correctly. Full behavioural tests of ds-auth itself live in that
package's own test suite.

Each test reloads ``app.settings`` and ``app.main`` with monkeypatched env;
the ``_reset_main`` autouse fixture undoes the mutation after each test so
subsequent tests in the suite still see the default auth-OFF app.
"""

from __future__ import annotations

import importlib
import re

import pytest

_AUTH_ENV_VARS = (
    "DS__AUTH__ENABLED",
    "DS__AUTH__JWKS_URL",
    "DS__AUTH__POLICY_ENGINE_URL",
    "DS__AUTH__JWT_ISSUER",
    "DS__AUTH__JWT_AUDIENCE",
)


def _reload_app():
    """Reload settings + main so env changes take effect."""
    import app.settings as settings_mod

    importlib.reload(settings_mod)
    import app.main as main_mod

    importlib.reload(main_mod)
    return main_mod


@pytest.fixture(autouse=True)
def _reset_main(monkeypatch):
    """Ensure every test starts and ends with the default (auth-off) main app.

    Without this, ``importlib.reload(main)`` during one test persists the
    middleware-wrapped app and breaks every subsequent route test in the suite.
    """
    for var in _AUTH_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    _reload_app()
    yield
    for var in _AUTH_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    _reload_app()


def test_auth_disabled_by_default():
    """With no DS__AUTH__* envs set, auth middleware is NOT installed."""
    main_mod = _reload_app()
    middleware_names = [m.cls.__name__ for m in main_mod.app.user_middleware]
    assert (
        "DataspaceAuthMiddleware" not in middleware_names
    ), f"auth middleware should be off by default; found: {middleware_names}"


def test_permission_map_covers_write_endpoints():
    """Every write-ish route (POST/DELETE outside catalog-browse) must have
    an entry — guards against adding a new mutator without a permission."""
    from app.rest_api.auth_config import PERMISSION_MAP, WRITE_PERMISSION

    write_entries = [
        (m, p) for (m, p, perm) in PERMISSION_MAP if perm == WRITE_PERMISSION
    ]
    paths = [p for (_m, p) in write_entries]
    # Datasets save + delete
    assert any("datasets" in p and "share" not in p for p in paths)
    # Share / unshare
    assert any("share" in p and "unshare" not in p for p in paths)
    assert any("unshare" in p for p in paths)
    # MMIO create + delete
    assert any(re.search(r"\^/mmio/\?\$", p) for p in paths)


def test_catalog_browse_is_read_not_write():
    """POST /catalog/ and /public-catalog/ carry a filter spec, not a
    mutation — they must map to catalog:read, not catalog:write."""
    from app.rest_api.auth_config import (
        PERMISSION_MAP,
        READ_PERMISSION,
        WRITE_PERMISSION,
    )

    perms = {(m, p): perm for (m, p, perm) in PERMISSION_MAP}
    assert perms.get(("POST", r"^/catalog/?$")) == READ_PERMISSION
    assert perms.get(("POST", r"^/public-catalog/?$")) == READ_PERMISSION
    # And at least one real write must still require catalog:write
    assert any(perm == WRITE_PERMISSION for perm in perms.values())


def test_public_paths_include_health_and_openapi():
    """Health, docs and OpenAPI must stay public even when auth is on."""
    from app.rest_api.auth_config import PUBLIC_PATHS

    assert "/health-check" in PUBLIC_PATHS
    assert "/health-check/" in PUBLIC_PATHS
    assert "/openapi.json" in PUBLIC_PATHS
    assert "/docs" in PUBLIC_PATHS


def test_auth_enabled_without_jwks_url_fails(monkeypatch):
    """Starting with DS__AUTH__ENABLED=true but no JWKS URL must fail loudly."""
    monkeypatch.setenv("DS__AUTH__ENABLED", "true")
    # Deliberately NOT setting DS__AUTH__JWKS_URL

    with pytest.raises(RuntimeError, match="DS__AUTH__JWKS_URL"):
        _reload_app()


def test_auth_enabled_installs_middleware(monkeypatch):
    """With all required DS__AUTH__* vars set, the middleware is wired.

    Only runs when the optional ``ds-auth`` extra is installed
    (``poetry install --extras auth``); CI's default job installs the base
    dependencies only, so this test is skipped there.
    """
    pytest.importorskip(
        "ds_auth",
        reason="ds-auth optional extra not installed "
        "(install with: poetry install --extras auth)",
    )
    monkeypatch.setenv("DS__AUTH__ENABLED", "true")
    monkeypatch.setenv("DS__AUTH__JWKS_URL", "http://login.test/.well-known/jwks.json")
    monkeypatch.setenv(
        "DS__AUTH__POLICY_ENGINE_URL", "http://ds-policy-engine.test:8000"
    )
    main_mod = _reload_app()
    middleware_names = [m.cls.__name__ for m in main_mod.app.user_middleware]
    assert "DataspaceAuthMiddleware" in middleware_names
