from typing import Annotated

from classy_fastapi import Routable, delete, get, post
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, Response

from app.core import entities, usecases
from app.core.repository import Repositories

from ..depends import get_repositories, get_user
from ..strings import FILE_ALREADY_EXISTS, FILE_NOT_FOUND, FILE_NOT_SELECTED
from ..tags import Tags


def get_usecases(
    repositories: Repositories = Depends(get_repositories),
) -> usecases.MMIOsUsecases:
    return usecases.MMIOsUsecases(repositories)


class MMIOsRoutes(Routable):
    @post(
        "/mmio/",
        operation_id="save_mmio_file",
        name="Save MMIO File",
        tags=[Tags.MMIO],
        status_code=status.HTTP_201_CREATED,
        response_class=Response,
        responses={
            status.HTTP_201_CREATED: {
                "description": "File uploaded successfully",
                "headers": {
                    "Location": {
                        "description": "URL to download the file",
                        "schema": {"type": "string"},
                        "example": "/mmio/mmio-sample.tar",
                    }
                },
            },
            status.HTTP_400_BAD_REQUEST: {
                "description": "No file selected for uploading",
            },
            status.HTTP_409_CONFLICT: {
                "description": "File already exists",
            },
        },
    )
    async def create(
        self,
        file: UploadFile,
        user: Annotated[entities.User, Depends(get_user)],
        usecases: usecases.MMIOsUsecases = Depends(get_usecases),
    ) -> Response:
        """Upload a MMIO file"""

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=FILE_NOT_SELECTED,
            )

        try:
            await usecases.create(file.file, file.filename, context={"user": user})
        except FileExistsError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=FILE_ALREADY_EXISTS,
            )

        return Response(
            status_code=status.HTTP_201_CREATED,
            headers={"Location": f"/mmio/{file.filename}"},
        )

    @get(
        "/mmio/{filename}/",
        operation_id="get_mmio_file",
        name="Get MMIO File",
        tags=[Tags.MMIO],
        response_class=FileResponse,
        responses={
            status.HTTP_200_OK: {
                "description": "Successful file retrieval",
                "content": {
                    "application/octet-stream": {
                        "schema": {
                            "type": "string",
                            "format": "binary",
                        }
                    }
                },
            },
            status.HTTP_404_NOT_FOUND: {"description": "File not found"},
        },
    )
    async def get(
        self,
        filename: str,
        user: Annotated[entities.User, Depends(get_user)],
        usecases: usecases.MMIOsUsecases = Depends(get_usecases),
    ) -> FileResponse:
        """Get a MMIO file"""

        try:
            file_path = await usecases.get(filename, context={"user": user})
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=FILE_NOT_FOUND,
            )

        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=filename,
        )

    @delete(
        "/mmio/{filename}/",
        operation_id="delete_mmio_file",
        name="Delete MMIO File",
        tags=[Tags.MMIO],
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            status.HTTP_404_NOT_FOUND: {"description": "File not found"},
        },
    )
    async def delete(
        self,
        filename: str,
        user: Annotated[entities.User, Depends(get_user)],
        usecases: usecases.MMIOsUsecases = Depends(get_usecases),
    ) -> None:
        """Delete a MMIO file"""

        try:
            await usecases.delete(filename, context={"user": user})
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=FILE_NOT_FOUND,
            )


routes = MMIOsRoutes()
