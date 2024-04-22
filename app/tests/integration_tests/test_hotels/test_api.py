from datetime import datetime

import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("location,date_from,date_to,status_code", [
    ("Алтай", "2023-07-01", "2023-07-08", 200),
    ("алтай", "2023-07-01", "2023-07-08", 200),
    ("Алтай", "2023-07-01", "2023-07-01", 400),
    ("Алтай", "2023-07-01", "2023-06-08", 400),
    ("Алтай", "2023-07-01", "2023-08-08", 400),
    ("Алтай", "2023--01", "2023-07-08", 422),
    ("Алтай", "2023-07-01", "2023-08", 422),
    ("Алsdgsdfgтай", "2023-07-01", "2023-07-08", 200)
])
async def test_get_hotels(location, date_from, date_to, status_code, authenticated_ac: AsyncClient):
    response = await authenticated_ac.get(
        f"/hotels/{location}",
        params={
            "date_from": date_from,
            "date_to": date_to,
        })

    assert response.status_code == status_code
