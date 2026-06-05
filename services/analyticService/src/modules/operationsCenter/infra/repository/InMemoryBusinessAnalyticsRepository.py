from src.infra.database import connect


class InMemoryBusinessAnalyticsRepository:
    def get_dashboard(self) -> dict:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) FILTER (WHERE routing_key LIKE 'agenda.appointment.created%') AS scheduled,
                        COUNT(*) FILTER (WHERE payload #>> '{data,status}' = 'finished') AS finished,
                        COUNT(*) FILTER (WHERE payload #>> '{data,status}' = 'canceled' OR routing_key LIKE 'agenda.appointment.deleted%') AS canceled,
                        COUNT(*) FILTER (WHERE routing_key = 'users.doctor.created') AS doctors,
                        COUNT(*) FILTER (WHERE routing_key = 'users.patient.created') AS patients
                    FROM analytic_events
                    """
                )
                stats = cursor.fetchone()
        scheduled = int(stats["scheduled"] or 0)
        finished = int(stats["finished"] or 0)
        canceled = int(stats["canceled"] or 0)
        doctors = int(stats["doctors"] or 0)
        patients = int(stats["patients"] or 0)
        return {
            "period": "last_30_days",
            "revenue": {
                "gross_amount": finished * 180.0,
                "pending_amount": max(scheduled - finished - canceled, 0) * 180.0,
                "canceled_amount": canceled * 180.0,
            },
            "appointments": {
                "scheduled": scheduled,
                "finished": finished,
                "canceled": canceled,
                "occupancy_rate": round(finished / scheduled, 2) if scheduled else 0,
            },
            "top_clinics": [
                {"clinic_id": "clinic-01", "name": "Matriz", "appointments": scheduled, "revenue": finished * 180.0},
            ],
            "alerts": [
                f"{doctors} doctors and {patients} patients indexed from events",
                "event-driven analytics online",
            ],
        }
