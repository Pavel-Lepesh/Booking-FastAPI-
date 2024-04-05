from pydantic import BaseModel


class SHotels(BaseModel):
    id: int
    name: str
    location: str
    services: list[str] | None
    rooms_quantity: int
    image_id: int | None
    rooms_left: int


class SHotel(BaseModel):
    id: int
    name: str
    location: str
    services: list[str] | None
    rooms_quantity: int
    image_id: int | None
