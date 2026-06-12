from src.infra.adapter.repository.base import SQLiteRepository


class AgendaRepository(SQLiteRepository):
    def create(self, agenda):
        data = agenda.model_dump() if hasattr(agenda, "model_dump") else agenda.dict()
        with self._db.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO agenda_records (paciente, profissional, data_hora, horario)
                VALUES (?, ?, ?, ?)
                RETURNING id
                """,
                (
                    data["paciente"],
                    data["profissional"],
                    data["data_hora"],
                    data["horario"],
                ),
            )
            return {"id": cursor.fetchone()["id"], **data}

    def list_all(self):
        with self._db.connect() as connection:
            rows = connection.execute(
                "SELECT id, paciente, profissional, data_hora, horario FROM agenda_records ORDER BY id"
            ).fetchall()
            return [dict(row) for row in rows]

    def get_by_id(self, agenda_id: int):
        with self._db.connect() as connection:
            row = connection.execute(
                "SELECT id, paciente, profissional, data_hora, horario FROM agenda_records WHERE id = ?",
                (agenda_id,),
            ).fetchone()
            return dict(row) if row else None

    def update(self, agenda_id: int, agenda):
        current = self.get_by_id(agenda_id)
        if not current:
            return None
        data = agenda.model_dump(exclude_unset=True) if hasattr(agenda, "model_dump") else agenda.dict(exclude_unset=True)
        updated = {**current, **data}
        with self._db.connect() as connection:
            connection.execute(
                """
                UPDATE agenda_records
                SET paciente = ?, profissional = ?, data_hora = ?, horario = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    updated["paciente"],
                    updated["profissional"],
                    updated["data_hora"],
                    updated["horario"],
                    agenda_id,
                ),
            )
        return updated

    def delete(self, agenda_id: int):
        return self._delete_by_id("agenda_records", str(agenda_id))
