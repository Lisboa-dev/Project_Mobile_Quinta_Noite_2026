import os

import pytest

pytestmark = pytest.mark.integration

REAL_SERVICES = os.getenv("TEST_USE_REAL_SERVICES", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

if REAL_SERVICES:
    psycopg2 = pytest.importorskip("psycopg2")
    PostgresContainer = pytest.importorskip("testcontainers.postgres").PostgresContainer
else:
    psycopg2 = None
    PostgresContainer = None


# =========================
# 🔧 CÓDIGO A SER TESTADO
# =========================

def soma(a: int, b: int) -> int:
    return a + b


def dividir(a: int, b: int) -> float:
    return a / b


def criar_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL
            );
        """)
    conn.commit()


def inserir_usuario(conn, nome: str):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO usuarios (nome) VALUES (%s) RETURNING id;",
            (nome,)
        )
        user_id = cur.fetchone()[0]
    conn.commit()
    return user_id


def listar_usuarios(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, nome FROM usuarios;")
        return cur.fetchall()


# =========================
# 🧪 FIXTURES
# =========================

@pytest.fixture(scope="session")
def postgres_url():
    """
    Sobe um container PostgreSQL para toda a sessão de testes.
    """
    if not REAL_SERVICES:
        pytest.skip("Set TEST_USE_REAL_SERVICES=true to run PostgreSQL container tests.")

    with PostgresContainer("postgres:15") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture(scope="function")
def db_conn(postgres_url):
    """
    Cria conexão nova para cada teste (isolamento).
    """
    conn = psycopg2.connect(postgres_url)
    criar_tabela(conn)

    yield conn

    conn.close()


# =========================
# 🧪 TESTES UNITÁRIOS
# =========================

def test_soma_simples():
    assert soma(2, 3) == 5


@pytest.mark.parametrize("a,b,resultado", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_soma_parametrizado(a, b, resultado):
    assert soma(a, b) == resultado


def test_divisao_normal():
    assert dividir(10, 2) == 5


def test_divisao_por_zero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)


# =========================
# 🧪 TESTES DE INTEGRAÇÃO (COM BANCO REAL)
# =========================

def test_inserir_usuario(db_conn):
    user_id = inserir_usuario(db_conn, "Matheus")

    usuarios = listar_usuarios(db_conn)

    assert len(usuarios) == 1
    assert usuarios[0][0] == user_id
    assert usuarios[0][1] == "Matheus"


def test_multiplos_usuarios(db_conn):
    inserir_usuario(db_conn, "Alice")
    inserir_usuario(db_conn, "Bob")

    usuarios = listar_usuarios(db_conn)

    nomes = [u[1] for u in usuarios]

    assert "Alice" in nomes
    assert "Bob" in nomes


def test_banco_isolado(db_conn):
    """
    Garante que cada teste começa limpo.
    """
    usuarios = listar_usuarios(db_conn)
    assert usuarios == []


# =========================
# 🧪 TESTE COM SETUP EXTRA
# =========================

@pytest.fixture
def usuario_padrao(db_conn):
    inserir_usuario(db_conn, "Default User")
    return db_conn


def test_usuario_padrao(usuario_padrao):
    usuarios = listar_usuarios(usuario_padrao)

    assert len(usuarios) == 1
    assert usuarios[0][1] == "Default User"
