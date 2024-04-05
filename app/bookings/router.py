from fastapi import APIRouter, Depends, status, BackgroundTasks
from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBookingInfo, SBooking
from app.users.dependencies import get_current_user
from app.users.models import Users
from datetime import date
from app.exceptions import RoomCannotBeBooked
from app.tasks.tasks import send_booking_confirmation_email


router = APIRouter(
    prefix='/bookings',
    tags=["Бронирования"]
)


@router.get("", status_code=status.HTTP_200_OK)
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBookingInfo]:
    return await BookingDAO.find_all_with_image(user_id=user.id)


@router.post("", status_code=status.HTTP_201_CREATED)
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
    background_tasks.add_task(send_booking_confirmation_email, booking_dict, user.email)
    return booking_dict


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)) -> None:
    await BookingDAO.delete(id=booking_id, user_id=user.id)
