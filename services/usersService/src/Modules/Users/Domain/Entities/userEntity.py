from dataclasses import dataclass
from typing import final
from ..valueObjects.Id import ID
from ..valueObjects.CargoVO import Cargo
from ..valueObjects.EmailVO import Email
from ..valueObjects.NomeVO import Nome
from ..valueObjects.PasswordVO import Password
from ..valueObjects.UserNomeVO import UserName


@dataclass
class User:
 

    def __init__(
        self,
        userName: str,
        email: str,
        name: str | None = None,
        nome: str | None = None,
        cargo: str | None = None,
        password: str | None = None,
        id: str | None = None,
        profile_image_url: str | None = None,
        profile_image_object: str | None = None,
        password_hashed: bool = False,
       
    ):
        self.id = ID(id) if id else None
        self.userName = UserName(userName)
        self.email = Email(email)
        self.name = Nome(name or nome or "")
        self.cargo = Cargo(cargo)
        if type(password) == str:
            self.password = Password(password if password_hashed else Password._hash_password(password))
        else:
            self.password = None
        self.profile_image_url = profile_image_url
        self.profile_image_object = profile_image_object

  
    @classmethod
    def create_user(cls, userName: str, email: str, name: str, password: str, profile_image_url = None, profile_image_object = None, **extra):
      
        return cls(
            userName=userName,
            email=email,
            name=name,
            password=Password._hash_password(password) ,
            id =ID.generate_id(),
            profile_image_url=profile_image_url,
            profile_image_object=profile_image_object,
            password_hashed=True,
            **extra
        )

    def to_dict(self) -> dict:
        cargo = self.cargo
        if isinstance(cargo, tuple) and len(cargo) == 1:
            cargo = cargo[0]
        cargo_value = getattr(cargo, "valor", None) or getattr(cargo, "value", cargo)
        return {
            "id": str(self.id) if self.id is not None else None,
            "userName": self.userName.value,
            "nome": self.name.value,
            "email": self.email.value,
            "senha": self.password.hash if self.password is not None else None,
            "cargo": cargo_value,
            "profile_image_url": self.profile_image_url,
            "profile_image_object": self.profile_image_object,
        }
        
      
