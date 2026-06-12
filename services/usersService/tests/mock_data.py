from uuid import NAMESPACE_URL, uuid5


MOCK_MEDIC_ID = str(uuid5(NAMESPACE_URL, "usersService/tests/dra.ana:ana@example.com"))

MOCK_MEDIC = {
    "userName": "dra.ana",
    "email": "ana@example.com",
    "name": "Ana Souza",
    "password": "Admin123!",
    "crm": "CRM-12345",
}

MOCK_ADMIN = {
    "userName": "admin",
    "email": "admin@example.com",
    "name": "Admin Root",
    "password": "Admin123!",
}
