from typing import Any

from fastapi import Response

from app.core.entities import Graph


class JSONLDResponse(Response):
    media_type = "application/ld+json"

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        if not isinstance(content, Graph):
            raise Exception(
                "The content must be an instance of Graph or a subclass thereof "
                "to generate a JSON-LD response."
            )
        content = content.to_json_ld()
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            **kwargs,
        )
