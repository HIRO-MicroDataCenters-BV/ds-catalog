from classy_fastapi import Routable, get
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.filters_usecases import FiltersUsecases
from app.rest_api.tags import Tags
from app.settings import Settings, get_settings


class FiltersRoutes(Routable):
    @get(
        "/catalog/filters/",
        operation_id="get_filters",
        name="Get Filters",
        tags=[Tags.Catalog],
        summary="Get filters",
        description=("Fetching the filter menu dynamically. "),
        response_class=JSONResponse,
        responses={
            200: {
                "description": "Successful Response",
                "content": {
                    "application/json": {
                        "example": {
                            "groups": [
                                {
                                    "id": "sociodemographics",
                                    "label": "Sociodemographics",
                                    "items": [
                                        {
                                            "id": "sociodemographics.age",
                                            "label": "Age",
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                },
            },
            status.HTTP_404_NOT_FOUND: {"description": "Filters file not found"},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "description": "Invalid filters.json"
            },
        },
    )
    async def get_filters(
        self,
        settings: Settings = Depends(get_settings),
    ) -> JSONResponse:
        usecase = FiltersUsecases(filters_file=settings.filters_file)

        try:
            payload = await usecase.get_filters()
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Filters configuration file not found",
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid filters.json",
            )

        return JSONResponse(content=payload)


routes = FiltersRoutes()
