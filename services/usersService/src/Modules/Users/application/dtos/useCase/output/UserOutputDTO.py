from dataclasses import dataclass


@dataclass(frozen=True)
class UserOutputDTO:
    id: str | None
    userName: str
    email: str
    name: str
    cargo: str | None
    profileImageUrl: str | None = None

    @classmethod
    def from_entity(cls, user):
        user_id = getattr(user.id, "id", user.id)
        name = getattr(user, "nome", getattr(user, "name", None))
        cargo = getattr(user, "cargo", None)
        if isinstance(cargo, tuple):
            cargo = cargo[0] if len(cargo) == 1 else None

        # ensure name is a string (dataclass requires str)
        name_value = getattr(name, "value", name)
        if name_value is None:
            name_value = ""

        cargo_value = getattr(cargo, "valor", None) or getattr(cargo, "value", cargo)
        if isinstance(cargo_value, tuple):
            cargo_value = cargo_value[0] if len(cargo_value) == 1 else None
        if cargo_value is not None:
            cargo_value = str(cargo_value)

        return cls(
            id=str(user_id) if user_id is not None else None,
            userName=getattr(user.userName, "value", user.userName),
            email=getattr(user.email, "value", user.email),
            name=name_value,
            cargo=cargo_value,
            profileImageUrl=getattr(user, "profile_image_url", None),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "userName": self.userName,
            "email": self.email,
            "name": self.name,
            "cargo": self.cargo,
            "profileImageUrl": self.profileImageUrl,
        }
