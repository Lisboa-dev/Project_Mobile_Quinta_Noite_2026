<<<<<<< HEAD
# Project_Mobile_Quinta_Noite_2026
Esse repositório é dedicado ao projeto da cadeira mobile cursada na unipe
=======
# Sistema de Agendamento Médico
**LEIA OS ARQUIVOS DA PASTA `Arquivos_Explicativos`**
## 1. Visão Geral

Este projeto consiste em um **Sistema de Agendamento Médico** baseado em:

* Arquitetura de Microserviços
* Clean Architecture
* Python
* Poetry (gerenciamento de dependências)
* Docker
* Docker Compose (orquestração)
* GitHub Actions (CI/CD)


---

## 2. Arquitetura Geral

O sistema é dividido em múltiplos microserviços, por exemplo:

* Serviço de Usuários
* Serviço de Médicos
* Serviço de Agendamentos
* Serviço de Notificações

Cada serviço é:

* Independente
* Containerizado
* Versionado separadamente

---

## 3. Clean Architecture

Cada microserviço segue a Clean Architecture, com separação clara de camadas.

Estrutura interna padrão de cada módulo:

```
service-name/
 ├── src/
 │   ├── domain/
 │   ├── application/
 │   ├── infra/
 │   └── api/
 ├── tests/
 ├── Dockerfile
 ├── pyproject.toml
 └── poetry.lock
```

### 3.1 Camada Domain

Contém:

* Entidades
* Regras de negócio puras
* Interfaces (contratos)

Não depende de frameworks.

### 3.2 Camada Application

Contém:

* Casos de uso
* DTOs
* Orquestração das regras

Depende apenas da camada Domain.

### 3.3 Camada Infra

Contém:

* Implementações de repositórios
* Conexão com banco
* Integrações externas

Depende de Application e Domain.

### 3.4 Camada API

Contém:

* Servidor (ex: FastAPI)
* Rotas
* Controllers
* Middlewares
* Dependências específicas de API

É a camada mais externa.

---

## 4. Gerenciamento com Poetry

Cada microserviço possui seu próprio:

* pyproject.toml
* poetry.lock

Responsabilidades:

* Gerenciar dependências isoladamente
* Garantir reprodutibilidade
* Definir scripts executáveis

Exemplo de scripts no pyproject.toml:

```toml
[tool.poetry.scripts]
start = "api.main:run"
test = "pytest"
```

Além disso, existe um **pyproject.toml na raiz** do projeto para:

* Scripts globais
* Automação
* Ferramentas compartilhadas

---

## 5. Dockerização

Cada módulo possui seu próprio Dockerfile.

Responsabilidades:

* Build isolado
* Instalação de dependências via Poetry
* Execução do serviço

Exemplo simplificado:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry
RUN poetry install --no-root

COPY . .

CMD ["poetry", "run", "start"]
```

---

## 6. Orquestração com Docker Compose

Existe um docker-compose.yml na raiz do projeto.

Responsabilidades:

* Subir todos os microserviços
* Configurar redes
* Configurar bancos de dados isolados
* Definir variáveis de ambiente

Estrutura simplificada:

```yaml
version: '3.9'

services:
  users:
    build: ./services/users
    ports:
      - "8001:8000"

  appointments:
    build: ./services/appointments
    ports:
      - "8002:8000"

  db_users:
    image: postgres:16

  db_appointments:
    image: postgres:16
```

Cada serviço possui seu próprio banco.

---

## 7. Testes

Cada módulo contém uma pasta:

```
tests/
```

Contém:

* Testes unitários (Domain)
* Testes de casos de uso (Application)
* Testes de integração (Infra/API)

Execução via:

```
poetry run pytest
```

---

## 8. CI/CD com GitHub Actions

O projeto utiliza GitHub Actions para:

* Rodar testes automaticamente
* Validar build dos containers
* Garantir qualidade antes de merge

Exemplo de pipeline:

* Checkout do código
* Setup Python
* Instalação do Poetry
* Instalação de dependências
* Execução dos testes
* Build da imagem Docker

Possível extensão futura:

* Versionamento semântico automático
* Publicação em registry
* Deploy automatizado

---

## 9. Benefícios da Arquitetura

* Alta coesão
* Baixo acoplamento
* Escalabilidade independente
* Facilidade para evoluir serviços separadamente
* Testabilidade elevada
* Organização clara por responsabilidade

---

## 10. Evoluções Futuras

* API Gateway
* Autenticação centralizada
* Observabilidade (logs estruturados + tracing)
* Mensageria para comunicação assíncrona
* Kubernetes para orquestração avançada

---

## 11. Documentações Oficiais e Referências

### Python

* Site oficial: [https://www.python.org/](https://www.python.org/)
* Documentação oficial: [https://docs.python.org/3/](https://docs.python.org/3/)
* Guia de ambientes virtuais: [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)

### Git

* Site oficial: [https://git-scm.com/](https://git-scm.com/)
* Documentação oficial: [https://git-scm.com/docs](https://git-scm.com/docs)
* Livro oficial gratuito (Pro Git): [https://git-scm.com/book/en/v2](https://git-scm.com/book/en/v2)

### GitHub

* Site oficial: [https://github.com/](https://github.com/)
* Documentação oficial: [https://docs.github.com/](https://docs.github.com/)
* GitHub Actions: [https://docs.github.com/en/actions](https://docs.github.com/en/actions)

### Docker

* Site oficial: [https://www.docker.com/](https://www.docker.com/)
* Documentação oficial: [https://docs.docker.com/](https://docs.docker.com/)
* Docker Compose: [https://docs.docker.com/compose/](https://docs.docker.com/compose/)

### Poetry

* Site oficial: [https://python-poetry.org/](https://python-poetry.org/)
* Documentação oficial: [https://python-poetry.org/docs/](https://python-poetry.org/docs/)
* PyProject (PEP 518/621): [https://peps.python.org/pep-0518/](https://peps.python.org/pep-0518/) e [https://peps.python.org/pep-0621/](https://peps.python.org/pep-0621/)

---

## 12. Como Rodar a Aplicação

Existem duas formas principais de executar o sistema: localmente com Poetry ou via Docker Compose.

---

### 12.1 Executando Localmente (Modo Desenvolvimento)

Pré-requisitos:

* Python 3.12+
* Poetry instalado
* Docker (caso utilize banco containerizado)

Passos para rodar um microserviço individualmente:

```bash
cd services/users
poetry install
poetry run start
```

Para rodar os testes do serviço:

```bash
poetry run pytest
```

Caso o banco esteja em container:

```bash
docker compose up db_users
```

---

### 12.2 Executando Todo o Sistema com Docker Compose

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

## 13. Tutoriais Práticos de Poetry

Esta seção contém um guia rápido para uso do Poetry no contexto do projeto.

---

### 13.1 Instalando o Poetry

Linux / macOS:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Windows (PowerShell):

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Verificar instalação:

```bash
poetry --version
```

---

### 13.2 Criando um Novo Projeto

```bash
poetry new nome-do-servico
```

Ou inicializando em um diretório existente:

```bash
poetry init
```

Isso criará o arquivo `pyproject.toml`.

---

### 13.3 Adicionando Dependências

Adicionar dependência de produção:

```bash
poetry add fastapi
```

Adicionar dependência de desenvolvimento:

```bash
poetry add --group dev pytest
```

---

### 13.4 Instalando Dependências

```bash
poetry install
```

Isso criará automaticamente o ambiente virtual e instalará as dependências definidas no `pyproject.toml`.

---

### 13.5 Executando Comandos no Ambiente Virtual

Executar script:

```bash
poetry run python src/api/main.py
```

### 13.6 Gerenciando Versões

Atualizar dependências:

```bash
poetry update
```

Exportar requirements (caso necessário):

```bash
poetry export -f requirements.txt --output requirements.txt
```

---

### 13.7 Boas Práticas com Poetry em Microserviços

* Cada microserviço deve ter seu próprio `pyproject.toml`.
* Não compartilhar ambientes virtuais entre serviços.
* Versionar sempre o `poetry.lock`.
* Usar grupos de dependências para separar produção e desenvolvimento.

---
>>>>>>> example
