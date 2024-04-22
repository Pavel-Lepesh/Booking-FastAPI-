import asyncio
from typing import Literal

from app.hotels.dao import HotelsDAO
from fastapi import APIRouter, status, UploadFile
from app.importer.utils import parse_csv


router = APIRouter(
    prefix="/import",
    tags=["Импорт данных"]
)


@router.post("/{table_name}", status_code=status.HTTP_201_CREATED)
async def import_hotels(table_name: Literal["hotels", "rooms"], file: UploadFile):
    data = parse_csv(table_name, file)
    tasks = [asyncio.create_task(HotelsDAO.add(**item)) for item in data]
    await asyncio.gather(*tasks)
