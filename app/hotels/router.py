import asyncio
from datetime import date

from fastapi import APIRouter, status
from fastapi_cache.decorator import cache

from app.hotels.dao import HotelsDAO
from app.hotels.schemas import SHotel, SHotels
from app.services import correct_date_check

router = APIRouter(
    prefix="/hotels",
    tags=['Поиск отелей и комнат']
)


@router.get("/{location}", status_code=status.HTTP_200_OK)
async def get_hotels(location: str, date_from: date, date_to: date) -> list[SHotels]:
    correct_date_check(date_from, date_to)
    hotels = await HotelsDAO.find_all(location, date_from, date_to)
    return hotels


@router.get("/id/{hotel_id}", status_code=status.HTTP_200_OK)
async def get_specific_hotel(hotel_id: int) -> SHotel:
    return await HotelsDAO.find_by_id(hotel_id)
