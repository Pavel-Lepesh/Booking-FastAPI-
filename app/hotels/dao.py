from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Hotels
from app.bookings.models import Bookings
from app.hotels.rooms.models import Rooms
from sqlalchemy import select, func, and_, or_
from datetime import date


class HotelsDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(cls, location: str, date_from: date, date_to: date):
        """
        WITH booked_rooms AS (
            SELECT hotel_id, COUNT(room_id) AS rooms_count
            FROM bookings
            JOIN rooms ON rooms.id = bookings.room_id
            JOIN hotels ON hotels.id = rooms.hotel_id
            WHERE
            (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
            (date_from <= '2023-05-15' AND date_to > '2023-05-15')
            GROUP BY hotel_id
        )

        SELECT hotels.id,
               hotels.name,
               hotels.location,
               hotels.services,
               hotels.rooms_quantity,
               hotels.image_id,
               hotels.rooms_quantity - COALESCE(rooms_count, 0) AS rooms_left
        FROM hotels
        JOIN rooms ON hotels.id = rooms.hotel_id
        LEFT JOIN booked_rooms ON hotels.id = booked_rooms.hotel_id
        WHERE hotels.location ILIKE '%алтай%'
        GROUP BY hotels.id, rooms_count;
        """
        async with async_session_maker() as session:
            booked_rooms = (
                select(Rooms.hotel_id, func.count(Bookings.room_id).label('rooms_count'))
                .select_from(Bookings)
                .join(Rooms, Rooms.id == Bookings.room_id)
                .join(Hotels, Hotels.id == Rooms.hotel_id)
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
                .group_by(Rooms.hotel_id)
            ).cte("booked_rooms")

            available_hotels = (
                select(Hotels.id,
                       Hotels.name,
                       Hotels.location,
                       Hotels.services,
                       Hotels.rooms_quantity,
                       Hotels.image_id,
                       (Hotels.rooms_quantity - func.coalesce(booked_rooms.c.rooms_count, 0)).label('rooms_left'))
                .select_from(Hotels)
                .join(Rooms, Hotels.id == Rooms.hotel_id)
                .join(booked_rooms, booked_rooms.c.hotel_id == Hotels.id, isouter=True)
                .where(Hotels.location.icontains(location))
                .group_by(Hotels.id, booked_rooms.c.rooms_count)
            )
            hotels = await session.execute(available_hotels)
            return hotels.mappings().all()
