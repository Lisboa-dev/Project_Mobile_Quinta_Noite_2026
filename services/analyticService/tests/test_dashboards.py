from importlib import import_module


doctor_module = import_module("src.modules.doctorDashboard.infra.repository.InMemoryDoctorAnalyticsRepository")
business_module = import_module("src.modules.operationsCenter.infra.repository.InMemoryBusinessAnalyticsRepository")


class FakeCursor:
    def __init__(self, row):
        self.row = row

    def execute(self, *_args, **_kwargs):
        return None

    def fetchone(self):
        return self.row

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class FakeConnection:
    def __init__(self, row):
        self.row = row

    def cursor(self):
        return FakeCursor(self.row)


class FakeConnect:
    def __init__(self, row):
        self.row = row

    def __enter__(self):
        return FakeConnection(self.row)

    def __exit__(self, *_args):
        return False


def test_doctor_dashboard_statistics(monkeypatch):
    monkeypatch.setattr(
        doctor_module,
        "connect",
        lambda: FakeConnect({"scheduled": 10, "finished": 8, "canceled": 1}),
    )

    dashboard = doctor_module.InMemoryDoctorAnalyticsRepository().get_dashboard("doctor-1")

    assert dashboard["productivity"]["scheduled_appointments"] == 10
    assert dashboard["patient_flow"]["no_show_rate"] == 0.1


def test_admin_dashboard_statistics(monkeypatch):
    monkeypatch.setattr(
        business_module,
        "connect",
        lambda: FakeConnect({"scheduled": 20, "finished": 15, "canceled": 2, "doctors": 3, "patients": 12}),
    )

    dashboard = business_module.InMemoryBusinessAnalyticsRepository().get_dashboard()

    assert dashboard["appointments"]["occupancy_rate"] == 0.75
    assert dashboard["revenue"]["gross_amount"] == 2700.0
