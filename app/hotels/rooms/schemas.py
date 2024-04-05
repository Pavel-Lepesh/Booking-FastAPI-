from pydantic import BaseModel


class SRooms(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str | None
    services: list[str] | None
    price: int
    quantity: int
    image_id: int | None
    total_cost: int
    rooms_left: int
