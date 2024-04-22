from datetime import date

from sqlalchemy import and_, func, or_, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class RoomsDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def find_all(cls, hotel_id: int, date_from: date, date_to: date):
        """
        WITH booked_rooms AS (
            SELECT room_id, COUNT(room_id) AS rooms_count
            FROM bookings
            JOIN rooms ON rooms.id = bookings.room_id
            WHERE
            (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
            (date_from <= '2023-05-15' AND date_to > '2023-05-15')
            GROUP BY room_id
        )

        SELECT id,
               hotel_id,
               name,
               description,
               services,
               price,
               quantity,
               image_id,
               (DATE('2023-06-20') - DATE('2023-05-15')) * price AS total_cost,
               quantity - COALESCE(rooms_count, 0) AS rooms_left
        FROM rooms
        LEFT OUTER JOIN booked_rooms ON rooms.id = booked_rooms.room_id
        WHERE hotel_id = 1;
        """

        async with async_session_maker() as session:
            booked_rooms = (
                select(Rooms.id, func.count(Rooms.id).label("rooms_count"))
                .select_from(Bookings)
                .join(Rooms, Rooms.id == Bookings.room_id)
                .where(
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from <= date_to
                        ),
                        and_(
                            Bookings.date_from <= date_from,
                            Bookings.date_to > date_from
                        )
                    )
                )
                .group_by(Rooms.id)
            ).cte("booked_rooms")

            available_rooms = (
                select(Rooms.id,
                       Rooms.hotel_id,
                       Rooms.name,
                       Rooms.description,
                       Rooms.services,
                       Rooms.price,
                       Rooms.quantity,
                       Rooms.image_id,
                       ((date_to - date_from).days * Rooms.price).label("total_cost"),
                       (Rooms.quantity - func.coalesce(booked_rooms.c.rooms_count, 0)).label("rooms_left"))
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.id == Rooms.id, isouter=True)
                .where(Rooms.hotel_id == hotel_id)
            )

            rooms = await session.execute(available_rooms)
            return rooms.mappings().all()
