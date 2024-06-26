from datetime import datetime

import pytest

from app.bookings.dao import BookingDAO


@pytest.mark.parametrize("user_id,room_id", [
    (1, 2),
    (1, 2),
    (2, 3),
    (2, 3)
])
async def test_add_and_get_booking(user_id, room_id):
    new_booking = await BookingDAO.add(
        user_id=user_id,
        room_id=room_id,
        date_from=datetime.strptime("2023-07-10","%Y-%m-%d"),
        date_to=datetime.strptime("2023-07-24", "%Y-%m-%d"),
    )

    assert new_booking.user_id == user_id
    assert new_booking.room_id == room_id

    new_booking = await BookingDAO.find_by_id(new_booking.id)

    assert new_booking is not None

    await BookingDAO.delete(id=new_booking.id)

    deleted_booking = await BookingDAO.find_by_id(new_booking.id)

    assert deleted_booking is None
