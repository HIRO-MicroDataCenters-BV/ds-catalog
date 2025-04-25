from pathlib import Path

import pytest


@pytest.fixture
def snapshot_for_class(snapshot, request):
    p = Path(snapshot.snapshot_dir)
    test_class_name = request.cls.__name__ if request.cls else "module"
    snapshot.snapshot_dir = p.parent / test_class_name / p.name
    return snapshot
