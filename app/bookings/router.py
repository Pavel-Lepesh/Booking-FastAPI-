from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from fastapi_versioning import version

from app.bookings.dao import BookingDAO
from app.bookings.models import Bookings
from app.bookings.schemas import SBooking, SBookingInfo
from app.database import async_session_maker
from app.exceptions import RoomCannotBeBooked
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix='/bookings',
    tags=["Бронирования"]
)


@router.get("", status_code=status.HTTP_200_OK)
@version(1)
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBookingInfo]:
    return await BookingDAO.find_all_with_image(user_id=user.id)


@router.post("", status_code=status.HTTP_201_CREATED)
@version(1)
async def add_booking(
        background_tasks: BackgroundTasks,
        room_id: int,
        date_from: date,
        date_to: date,
        user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBooked

    booking_dict = SBooking.model_validate(booking).model_dump()
    # celery option
    # send_booking_confirmation_email.delay(booking_dict, user.email)
    # background_tasks option
    #background_tasks.add_task(send_booking_confirmation_email, booking_dict, user.email)
    return booking_dict


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
@version(2)
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)) -> None:
    await BookingDAO.delete(id=booking_id, user_id=user.id)


@router.get("/example/orm")
async def get_noorm():
    async with async_session_maker() as session:
        query = (
            select(Bookings)
            # .options(selectinload(Rooms.hotel))
            .options(joinedload(Bookings.room))
        )

        res = await session.execute(query)
        res = res.scalars().all()
        res = jsonable_encoder(res)
        return res
