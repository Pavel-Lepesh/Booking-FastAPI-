from pydantic import BaseModel


class SHotels(BaseModel):
    name: str
    location: str
    services: list[str] | None
    rooms_quantity: int
    image_id: int | None


SCHEMAS_VALIDATE = {"hotels": SHotels}
