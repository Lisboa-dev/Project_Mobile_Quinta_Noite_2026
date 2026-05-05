class Nome:
    def __init__(self, valor: str):
        valor = valor.strip()
        if not valor:
            raise ValueError("O nome não pode ser vazio")
        if len(valor) < 2:
            raise ValueError("O nome deve ter pelo menos 2 caracteres")
        self.valor = valor

    def __str__(self):
        return self.valor

    def __repr__(self):
        return f"Nome('{self.valor}')"