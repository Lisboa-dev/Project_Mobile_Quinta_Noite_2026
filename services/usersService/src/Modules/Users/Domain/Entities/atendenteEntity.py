from .UserEntity import User


class Atendente(User):
    def __init__(
        self,
        userName: str,
        email: str,
        name: str,
        cpf: str,
        password: str | None = None,
        id: str | None = None,
        profile_image_url: str | None = None,
        profile_image_object: str | None = None,
    ):
        super().__init__(
            userName=userName,
            email=email,
            name=name,
            password=password,
            id=id,
            profile_image_url=profile_image_url,
            profile_image_object=profile_image_object,
        )
        self.cargo = "ATENDENTE",
        self.cpf = cpf
        