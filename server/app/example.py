from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ExampleResponse(BaseModel):
    """Example data"""

    value: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "value": "test value",
                }
            ]
        }
    }


@router.get(
    "/",
    operation_id="example__get",
    summary="Example endpoint",
)
async def read_root() -> ExampleResponse:
    """Example endpoint that returns test data"""
    return ExampleResponse(value="Hello World")
