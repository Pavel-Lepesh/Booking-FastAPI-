from fastapi import APIRouter, status
from datetime import date
from app.hotels.dao import HotelsDAO
from app.hotels.schemas import SHotels, SHotel
from fastapi_cache.decorator import cache
import asyncio


router = APIRouter(
    prefix="/hotels",
    tags=['Поиск отелей и комнат']
)


@router.get("/{location}", status_code=status.HTTP_200_OK)
@cache(expire=30)
async def get_hotels(location: str, date_from: date, date_to: date) -> list[SHotels]:
    await asyncio.sleep(3)
    hotels = await HotelsDAO.find_all(location, date_from, date_to)
    return hotels


@router.get("/id/{hotel_id}", status_code=status.HTTP_200_OK)
async def get_specific_hotel(hotel_id: int) -> SHotel:
    return await HotelsDAO.find_by_id(hotel_id)
