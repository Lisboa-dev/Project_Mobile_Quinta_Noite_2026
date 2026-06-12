# Guia de Comandos — Projeto com Poetry, FastAPI e Mypy

Este documento reúne os principais comandos para criar, configurar e executar um projeto utilizando **Poetry**, **FastAPI**, **Mypy** e **pytest**.

---

## 1. Instalar o Poetry

```bash
pip install poetry
```

Verificar instalação:

```bash
poetry --version
```

---

## 2. Criar um novo projeto

```bash
poetry new nome_do_projeto
```

Ou iniciar em um diretório existente:

```bash
poetry init
```

Entrar no diretório:

```bash
cd nome_do_projeto
```

---

## 3. Criar ambiente virtual

```bash
poetry install
```

---

## 4. Adicionar dependências

### FastAPI

```bash
poetry add fastapi
```

### Uvicorn (servidor ASGI)

```bash
poetry add uvicorn
```

### Mypy (como dependência de desenvolvimento)

```bash
poetry add --group dev mypy
```

---

## 5. Estrutura básica do projeto

Exemplo de estrutura:

```
nome_do_projeto/
├── pyproject.toml
├── nome_do_projeto/
│   └── main.py
└── tests/
```

---

## 6. Exemplo básico de aplicação FastAPI

`main.py`

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello World"}
```

---

## 7. Executar a aplicação

```bash
poetry run uvicorn nome_do_projeto.main:app --reload
```

---

## 8. Executar o Mypy

Verificação simples:

```bash
poetry run mypy .
```

Criar arquivo de configuração opcional:

`mypy.ini`

```ini
[mypy]
python_version = 3.11
strict = True
ignore_missing_imports = True
```

Executar novamente:

```bash
poetry run mypy nome_do_projeto
```

---

## 9. Scripts no pyproject.toml

Você pode adicionar atalhos no `pyproject.toml`:

```toml
[tool.poetry.scripts]
start = "uvicorn nome_do_projeto.main:app --reload"
check = "mypy nome_do_projeto"
```

Executar:

```bash
poetry run start
poetry run check
```

---

## 10. Atualizar dependências

```bash
poetry update
```

---

## 11. Exportar requirements.txt (opcional)

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

---

## 12. Remover dependência

```bash
poetry remove nome_da_dependencia
```

---

## 13. Ver dependências instaladas

```bash
poetry show
```

---

# Fluxo Resumido

```bash
poetry new api
cd api
poetry add fastapi uvicorn
poetry add --group dev mypy
poetry install
poetry run uvicorn api.main:app --reload
poetry run mypy .
```

---

# 14. Como fazer o Poetry rodar scripts no terminal

Existem **duas formas corretas** de rodar scripts com Poetry:

## ✅ 1) Usando `poetry run` (forma mais simples)

Você pode executar qualquer comando instalado no ambiente virtual assim:

```bash
poetry run python main.py
poetry run uvicorn api.main:app --reload
poetry run mypy .
```

Isso garante que o comando será executado dentro do ambiente virtual gerenciado pelo Poetry.

---

## ✅ 2) Criando comandos próprios (entry points)

No `pyproject.toml`, você pode definir comandos que chamam **funções Python**, não comandos shell diretos:

```toml
[tool.poetry.scripts]
start = "api.main:main"
```

E no seu `main.py`:

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()


def main() -> None:
    uvicorn.run("api.main:app", reload=True)
```

Agora você pode executar:

```bash
poetry run start
```

⚠️ Importante: `tool.poetry.scripts` funciona como `console_scripts` do setuptools — ele precisa apontar para uma função Python executável.

---

## ✅ 3) Criando "atalhos" para comandos (melhor prática)

Se você quiser criar atalhos como `start`, `check`, `lint`, etc., uma abordagem mais limpa é usar plugins como **taskipy**:

```bash
poetry add --group dev taskipy
```

No `pyproject.toml`:

```toml
[tool.taskipy.tasks]
start = "uvicorn api.main:app --reload"
check = "mypy ."
```

Executar:

```bash
poetry run task start
poetry run task check
```

Essa abordagem é mais flexível para projetos maiores.

---

Documento base para projetos Python modernos com tipagem estática e API REST utilizando FastAPI.


* **mypy** → verificação de tipos (análise estática)
* **pytest** → execução de testes (validação de comportamento)

Juntas, elas ajudam a evitar bugs antes e depois da execução do código.

---

# 🧠 Parte 1 — Mypy (Tipagem Estática)

## O que é?

O **mypy** é um verificador de tipos que analisa seu código sem executá-lo.

Ele garante que os tipos definidos são respeitados.

---

## 📦 Instalação

```bash
pip install mypy
```

---

## ⚙️ Uso básico

```bash
mypy arquivo.py
```

Ou no projeto inteiro:

```bash
mypy .
```

---

## ✍️ Tipagem básica

```python
def soma(a: int, b: int) -> int:
    return a + b
```

---

## ❌ Exemplo de erro detectado

```python
def soma(a: int, b: int) -> int:
    return a + b

resultado = soma(2, "3")  # erro de tipo
```

---

## 🧩 Tipos comuns

### Lista

```python
from typing import List

def dobrar(valores: List[int]) -> List[int]:
    return [v * 2 for v in valores]
```

### Dicionário

```python
from typing import Dict

def get_nome(usuario: Dict[str, str]) -> str:
    return usuario["nome"]
```

### Opcional

```python
from typing import Optional

def buscar_nome() -> Optional[str]:
    return None
```

### União (Python moderno)

```python
def processar(valor: int | str) -> str:
    return str(valor)
```

---

## ⚙️ Configuração recomendada

Crie um arquivo `mypy.ini`:

```ini
[mypy]
python_version = 3.11
strict = True
```

---

## ⚠️ Boas práticas

* Sempre tipar retorno de funções
* Evitar uso excessivo de `Any`
* Usar modo `strict`
* Tipar interfaces externas (APIs, JSON)

---

# 🧪 Parte 2 — Pytest (Testes Automatizados)

## O que é?

O **pytest** é uma ferramenta para escrever e executar testes de forma simples e poderosa.

---

## 📦 Instalação

```bash
pip install pytest
```

---

## ⚙️ Estrutura de projeto

```
projeto/
│
├── app/
│   └── calculo.py
│
└── tests/
    └── test_calculo.py
```

---

## ✍️ Exemplo básico

```python
# calculo.py

def soma(a, b):
    return a + b
```

```python
# test_calculo.py

def test_soma():
    assert soma(2, 3) == 5
```

---

## ▶️ Executar testes

```bash
pytest
```

---

## 🧪 Testando exceções

```python
import pytest

def dividir(a, b):
    if b == 0:
        raise ValueError("Divisão por zero")
    return a / b


def test_divisao_por_zero():
    with pytest.raises(ValueError):
        dividir(10, 0)
```

---

## 🔁 Fixtures (reutilização)

```python
import pytest

@pytest.fixture
def dados():
    return [1, 2, 3]


def test_lista(dados):
    assert sum(dados) == 6
```

---

## ⚠️ Boas práticas

* Testar casos de sucesso e erro
* Evitar dependências externas reais
* Manter testes independentes
* Nomear testes claramente

---

# 🔗 Integração Mypy + Pytest

Use ambos no fluxo de desenvolvimento:

```bash
pytest && mypy .
```

---

## 🧠 Diferença fundamental

| Ferramenta | O que valida  |
| ---------- | ------------- |
| mypy       | Tipos         |
| pytest     | Comportamento |

---

# 🚀 Conclusão

* **mypy** evita erros antes da execução
* **pytest** garante que o sistema funciona corretamente
* Usar os dois juntos aumenta drasticamente a qualidade do código

---

# 📚 Próximos passos

* coverage.py (cobertura de testes)
* unittest.mock (mocks)
* integração contínua (CI/CD)
* Testcontainers (testes com ambiente real)

