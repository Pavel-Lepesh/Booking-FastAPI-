from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from datetime import date
from sqlalchemy import select, func, and_, or_, insert

from app.database import engine, async_session_maker
from app.hotels.rooms.models import Rooms


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def find_all_with_image(cls, user_id: int):
        async with async_session_maker() as session:
            bookings = (
                select(Bookings.__table__.columns,
                       Rooms.__table__.columns)
                .select_from(Bookings)
                .join(Rooms, Bookings.room_id == Rooms.id)
                .where(Bookings.user_id == user_id)
            )
            user_bookings = await session.execute(bookings)
            return user_bookings.mappings().all()

    @classmethod
    async def add(
            cls,
            user_id: int,
            room_id: int,
            date_from: date,
            date_to: date
    ):
        """
        WITH booked_rooms AS (
            SELECT * FROM bookings
            WHERE room_id = 1 AND (
            (date_from >= '2033-05-15' AND date_from <= '2033-06-20') OR
            (date_from <= '2033-05-15' AND date_to > '2033-06-20') )
        )

        SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = 1
        GROUP BY rooms.quantity, booked_rooms.room_id;
        """
        async with async_session_maker() as session:
            booked_rooms = select(Bookings).where(
               and_(
                   Bookings.room_id == room_id,
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
            ).cte("booked_rooms")

            get_rooms_left = (
                select((Rooms.quantity - func.count(booked_rooms.c.room_id)).label("rooms_left"))
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                .where(Rooms.id == room_id)
                .group_by(Rooms.quantity, booked_rooms.c.room_id)
            )

            # print(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))
            rooms_left = await session.execute(get_rooms_left)
            rooms_left: int = rooms_left.scalar()

            if rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_booking = insert(Bookings).values(
                    room_id=room_id,
                    user_id=user_id,
                    date_from=date_from,
                    date_to=date_to,
                    price=price
                ).returning(Bookings)

                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.scalar()
            else:
                return None
