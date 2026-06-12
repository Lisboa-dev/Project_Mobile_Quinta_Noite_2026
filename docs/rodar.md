
Na raiz do projeto:

```bash
docker compose up --build
```

Isso irá:

* Buildar todas as imagens
* Subir todos os microserviços
* Subir todos os bancos de dados
* Criar a rede interna entre containers

Para rodar em modo detached:

```bash
docker compose up -d
```

Para subir tudo reconstruindo as imagens:

```bash
docker compose up -d --build
```

Se quiser subir tambem o RabbitMQ local do projeto:

```bash
docker compose --profile local-rabbitmq up -d --build
```

Por padrao, o RabbitMQ local fica opcional. Para usar um RabbitMQ global, configure a variavel `RABBITMQ_URL` no `.env`.

Para verificar o status dos containers:

```bash
docker compose ps
```

Para parar os serviços:

```bash
docker compose down
```

---

### 12.2.1 Rodando Todos os Testes

Com as dependencias instaladas localmente na raiz do projeto, rode a suite completa:

```bash
poetry run task test-all
```

Para rodar usando os containers que ja estao ligados, execute um servico por vez:

```bash
docker compose exec agenda-service pytest tests
docker compose exec users-service pytest tests
docker compose exec auth-service pytest tests
docker compose exec notificacao-service pytest tests
docker compose exec analytic-service pytest tests
```

No PowerShell, para rodar todos em sequencia e parar no primeiro erro:

```powershell
docker compose exec agenda-service pytest tests; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose exec users-service pytest tests; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose exec auth-service pytest tests; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose exec notificacao-service pytest tests; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose exec analytic-service pytest tests; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

Para incluir testes marcados como integracao no runner global:

```bash
poetry run python tests/run_tests.py --include-integration
```

---

### 12.3 Executando Scripts Globais da Raiz

Caso exista um `pyproject.toml` na raiz com scripts definidos:

```bash
poetry install
poetry run <nome-do-script>
```

Exemplo:

```bash
poetry run lint
poetry run test-all
```

---

### 12.4 Acessando a API

Após subir os serviços, use estas base URLs:

| Servico | Base URL via Traefik | Porta direta |
| --- | --- | --- |
| Auth | `http://localhost/auth` | `http://localhost:8000` |
| Agenda | `http://localhost/agenda` | `http://localhost:8001` |
| Users | `http://localhost/users` | `http://localhost:8002` |
| Notification | `http://localhost/notification` | `http://localhost:8003` |
| Analytics | `http://localhost/analytics` | `http://localhost:8005` |
| OpenFGA API | `http://localhost:8090` | `http://localhost:8090` |
| OpenFGA Playground | `http://localhost:3000` | `http://localhost:3000` |
| MinIO API | `http://localhost:9000` | `http://localhost:9000` |
| MinIO Console | `http://localhost:9001` | `http://localhost:9001` |
| Traefik Dashboard | `http://localhost:8080` | `http://localhost:8080` |

Documentacao FastAPI, quando habilitada:

```
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
http://localhost:8005/docs
```

Para acessar via Traefik, adicione `/docs` na base URL do servico quando a rota estiver exposta.

A documentacao detalhada de endpoints, parametros, bodies e respostas esperadas esta em:

```text
docs/api-endpoints.md
```

---

Para acessar o Grafana, ele precisa subir com o profile de observabilidade.

Na raiz do projeto:

docker compose --profile observability up -d grafana prometheus otel-collector
Depois acesse:

http://localhost:3001
Login padrão pelo docker-compose.yml:

usuario: admin
senha: admin
Para conferir se subiu:

docker compose ps grafana