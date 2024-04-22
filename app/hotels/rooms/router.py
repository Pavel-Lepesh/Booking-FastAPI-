from datetime import date

from fastapi import status

from app.hotels.rooms.dao import RoomsDAO
from app.hotels.rooms.schemas import SRooms
from app.hotels.router import router


@router.get("/{hotel_id}/rooms", status_code=status.HTTP_200_OK)
async def get_rooms(hotel_id: int, date_from: date, date_to: date) -> list[SRooms]:
    return await RoomsDAO.find_all(hotel_id, date_from, date_to)
