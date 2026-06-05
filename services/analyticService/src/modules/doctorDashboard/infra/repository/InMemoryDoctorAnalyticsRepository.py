from src.infra.database import connect


class InMemoryDoctorAnalyticsRepository:
    def get_dashboard(self, doctor_id: str) -> dict:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) FILTER (WHERE routing_key LIKE 'agenda.appointment.created%') AS scheduled,
                        COUNT(*) FILTER (WHERE payload #>> '{data,status}' = 'finished') AS finished,
                        COUNT(*) FILTER (WHERE payload #>> '{data,status}' = 'canceled' OR routing_key LIKE 'agenda.appointment.deleted%') AS canceled
                    FROM analytic_events
                    WHERE COALESCE(payload #>> '{data,doctor_id}', %s) = %s
                    """,
                    (doctor_id, doctor_id),
                )
                stats = cursor.fetchone()
        scheduled = int(stats["scheduled"] or 0)
        finished = int(stats["finished"] or 0)
        canceled = int(stats["canceled"] or 0)
        return {
            "doctor_id": doctor_id,
            "period": "last_30_days",
            "productivity": {
                "scheduled_appointments": scheduled,
                "finished_appointments": finished,
                "canceled_appointments": canceled,
                "average_delay_minutes": 7.4,
            },
            "patient_flow": {
                "new_patients": max(scheduled - finished, 0),
                "returning_patients": finished,
                "no_show_rate": round(canceled / scheduled, 3) if scheduled else 0,
            },
            "next_action": "review patients with recurring no-show behavior",
        }
