import pytest

from src.services.authorization import OpenFGAAuthorizationService


@pytest.mark.parametrize(
    ("path", "method", "permission"),
    [
        ("/users/users/user-1", "GET", "users.self.read"),
        ("/users/medics", "GET", "users.medics.read"),
        ("/users/medics/medic-1", "GET", "users.medics.read"),
        ("/users/pacients", "GET", "users.pacients.read"),
        ("/users/pacients/pacient-1", "GET", "users.pacients.read"),
        ("/users/admins", "GET", "users.admins.read"),
        ("/users/admins/doctors", "POST", "users.doctors.create"),
        ("/users/medics", "POST", "users.doctors.create"),
        ("/agenda/appointments/apt-1", "PATCH", "agenda.appointments.manage"),
        ("/notification/notifications/patients/patient-1/bell", "GET", "notifications.patient.read"),
        ("/notification/notifications/doctors/doctor-1", "GET", "notifications.doctor.read"),
        ("/notification/notifications/admins/bell", "GET", "notifications.admin.read"),
        ("/analytics/operations/business/dashboard", "GET", "analytics.operations.read"),
        ("/analytics/doctors/doctor-1/dashboard", "GET", "analytics.doctors.read"),
    ],
)
def test_route_permission_mapping(path, method, permission):
    service = OpenFGAAuthorizationService()

    assert service._route_permission(path, method) == permission


def test_route_permission_returns_none_for_unmapped_route():
    service = OpenFGAAuthorizationService()

    assert service._route_permission("/users/health", "GET") is None
