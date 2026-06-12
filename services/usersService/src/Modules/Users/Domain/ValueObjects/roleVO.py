class Role:
    def __init__(self, value: str | None = None):
        self.value = (value or "").strip().upper() or None

    @property
    def valor(self) -> str | None:
        return self.value

    def __str__(self) -> str:
        return self.value or ""
