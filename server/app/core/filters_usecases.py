from typing import Any

import json
from pathlib import Path


class FiltersUsecases:
    def __init__(self, filters_file: str) -> None:
        self._path = Path(filters_file).resolve()

    async def get_filters(self) -> dict[str, Any]:
        if not self._path.exists():
            raise FileNotFoundError(str(self._path))

        try:
            with self._path.open(encoding="utf-8") as f:
                payload = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid filters.json: {exc}") from exc

        if (
            not isinstance(payload, dict)
            or "groups" not in payload
            or not isinstance(payload["groups"], list)
        ):
            raise ValueError("filters.json must be an object with a 'groups' array")

        return payload
