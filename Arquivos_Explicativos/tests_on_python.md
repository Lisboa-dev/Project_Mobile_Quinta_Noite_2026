# 🧪 Guia Completo de Testes em Python com Pytest

## 📌 Introdução

Testes automatizados são essenciais para garantir que seu código funcione corretamente e continue funcionando conforme evolui.

Em Python, a ferramenta mais popular para isso é o **pytest**.

---

## ⚙️ Instalação

```bash
poetry add pytest 
```
se usar pip em vez de poetry
```bash
pip install pytest
```
---

## 📁 Estrutura recomendada

```
project/
│
├── src/
│   └── app.py
│
├── tests/
│   └── test_app.py
```

---

## 🧠 Primeiro exemplo

### Código

```python
# app.py

def soma(a, b):
    return a + b
```

### Teste

```python
# test_app.py

from app import soma

def test_soma():
    assert soma(2, 3) == 5
```

### Executar

```bash
pytest
```

---

## 🔥 Parametrização

Permite testar vários cenários com menos código.

```python
import pytest
from app import soma

@pytest.mark.parametrize("a,b,resultado", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_soma_parametrizado(a, b, resultado):
    assert soma(a, b) == resultado
```

---

## ⚠️ Testando exceções

```python
import pytest

def dividir(a, b):
    return a / b


def test_divisao_por_zero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

---

## 🧩 Fixtures (preparação de ambiente)

```python
import pytest

@pytest.fixture
def dados():
    return (2, 3)


def test_soma_fixture(dados):
    a, b = dados
    assert a + b == 5
```

---

## 🧪 Organização de testes

```
tests/
├── unit/
├── integration/
└── e2e/
```

* **unit**: funções isoladas
* **integration**: banco, APIs
* **e2e**: sistema completo

---

## ⚙️ Configuração (pytest.ini)

```ini
[pytest]
testpaths = tests
```

---

## 🚀 Comandos úteis

```bash
pytest -v                # modo verboso
pytest -k "nome"        # filtrar testes
pytest tests/unit/       # rodar pasta específica
pytest arquivo.py        # rodar arquivo
```

---

## 🧠 Boas práticas

* Nomeie testes claramente
* Teste apenas um comportamento por vez
* Evite dependência entre testes
* Teste erros também

---

## ❌ Erros comuns

* Não usar prefixo `test_`
* Testes muito grandes
* Não isolar dados
* Depender de estado global

---

## 🔥 Próximos passos

* pytest-cov (cobertura de código)
* hypothesis (testes inteligentes)
* testcontainers (testes com banco real)

# 🧪📦 Guia de Testcontainers em Python (com Pytest)

## 📌 O que é Testcontainers?

**Testcontainers** é uma biblioteca que permite subir serviços reais (como bancos de dados) em containers automaticamente durante a execução dos testes.

> Você não precisa escrever `docker-compose` — a biblioteca gerencia tudo por baixo dos panos.

---

## ⚠️ Pré-requisitos

* Docker instalado e rodando
* Python 3.9+

Verifique o Docker:

```bash
docker ps
```

---

## ⚙️ Instalação

```bash
pip install pytest testcontainers psycopg2-binary
```

ou
```bash
poetry add pytest testcontainers psycopg2-binary
```

---

## 🚀 Primeiro exemplo (PostgreSQL)

```python
from testcontainers.postgres import PostgresContainer
import psycopg2


def test_conexao_basica():
    with PostgresContainer("postgres:15") as postgres:
        conn = psycopg2.connect(postgres.get_connection_url())

        cur = conn.cursor()
        cur.execute("SELECT 1")

        assert cur.fetchone()[0] == 1
```

---

## 🔁 Como funciona internamente

1. Sobe um container PostgreSQL
2. Gera uma URL de conexão
3. Executa o teste
4. Derruba o container automaticamente

---

## 🧩 Usando com Pytest (forma recomendada)

### Fixture básica

```python
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture
def postgres_url():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres.get_connection_url()
```

---

### Usando a fixture

```python
def test_db(postgres_url):
    import psycopg2

    conn = psycopg2.connect(postgres_url)
    cur = conn.cursor()

    cur.execute("SELECT 1")
    assert cur.fetchone()[0] == 1
```

---

## 🔥 Melhorando performance (escopo)

```python
@pytest.fixture(scope="session")
def postgres_url():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres.get_connection_url()
```

* `function`: container por teste (mais isolado)
* `session`: um container para todos os testes (mais rápido)

---

## 🧪 Conexão isolada por teste

```python
@pytest.fixture
def db_conn(postgres_url):
    import psycopg2

    conn = psycopg2.connect(postgres_url)
    yield conn
    conn.close()
```

---

## 🧱 Criando estrutura no banco

```python
def criar_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT
            );
        """)
    conn.commit()
```

---

## 🧪 Teste de integração real

```python
def test_insert(db_conn):
    criar_tabela(db_conn)

    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO users (name) VALUES ('Matheus')")
    db_conn.commit()

    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM users")
        total = cur.fetchone()[0]

    assert total == 1
```

---

## 🧠 Boas práticas

* Use containers apenas em testes de integração
* Mantenha testes unitários sem dependências externas
* Limpe dados entre testes
* Use fixtures para reutilização

---

## ⚠️ Erros comuns

* Esquecer de iniciar o Docker
* Subir container por teste sem necessidade
* Não fechar conexões
* Testes lentos por má configuração

---

## 🔥 Quando usar Testcontainers?

Use quando precisar de:

* Banco de dados real
* Cache (Redis)
* Filas (Kafka, RabbitMQ)
* Ambiente próximo ao de produção

---

## ❌ Quando NÃO usar

* Funções simples
* Testes unitários
* Lógica pura

---

## 🚀 Próximos passos

* Integrar com FastAPI
* Usar com CI (GitHub Actions)
* Testar múltiplos serviços (DB + Redis)
