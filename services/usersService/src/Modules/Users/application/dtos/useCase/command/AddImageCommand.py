from dataclasses import dataclass


@dataclass(frozen=True)
class AddImageCommand:
    user_id: int
    image_url: str
    image_object: str
    triggered_by_id: str | None = None
