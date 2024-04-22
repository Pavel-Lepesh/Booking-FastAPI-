import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("room_id,date_from,date_to,booked_rooms,status_code", [
    (4, "2030-05-01", "2030-05-15", 3, 201),
    (4, "2030-05-02", "2030-05-16", 4, 201),
    (4, "2030-05-03", "2030-05-17", 5, 201),
    (4, "2030-05-04", "2030-05-18", 6, 201),
    (4, "2030-05-05", "2030-05-19", 7, 201),
    (4, "2030-05-06", "2030-05-20", 8, 201),
    (4, "2030-05-07", "2030-05-21", 9, 201),
    (4, "2030-05-08", "2030-05-22", 10, 201),
    (4, "2030-05-09", "2030-05-23", 10, 409),
    (4, "2030-05-10", "2030-05-24", 10, 409),
])
async def test_add_and_get_booking(
    room_id, date_from, date_to, booked_rooms, status_code, authenticated_ac: AsyncClient
):
    response = await authenticated_ac.post("/bookings", params={
        "room_id": room_id,
        "date_from": date_from,
        "date_to": date_to,
    })

    assert response.status_code == status_code

    response = await authenticated_ac.get("/bookings")
    assert len(response.json()) == booked_rooms


@pytest.mark.parametrize("list_bookings,len_content,status_code,delete_status_code", [
    ([1, 2], 2, 200, 204)
])
async def test_get_and_delete_user_bookings(list_bookings: list,
                                            len_content: int,
                                            status_code: int,
                                            delete_status_code: int,
                                            authenticated_ac: AsyncClient):
    get_response = await authenticated_ac.get("/bookings")

    assert get_response.status_code == status_code
    assert len(get_response.json()) == len_content

    for booking_id in list_bookings:
        delete_response = await authenticated_ac.delete(f"bookings/{booking_id}")

        assert delete_response.status_code == delete_status_code

    get_response = await authenticated_ac.get("/bookings")

    assert get_response.status_code == status_code
    assert len(get_response.json()) == 0
