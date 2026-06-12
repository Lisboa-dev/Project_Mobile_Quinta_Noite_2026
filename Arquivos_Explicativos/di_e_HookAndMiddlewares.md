# FastAPI -- Depends, Factory, Middleware, Hooks, `yield` e `call_next`

Este documento explica **como funcionam os principais mecanismos de
execução e injeção de dependências no FastAPI**, abordando:

1.  `Depends`
2.  Factory
3.  Middlewares
4.  Hooks (dependencies)
5.  `yield`
6.  `await call_next`

O objetivo é entender **como controlar a criação de objetos e o fluxo de
execução da requisição**.

------------------------------------------------------------------------

# 1. Depends

`Depends` é o **sistema de injeção de dependência nativo do FastAPI**.

Ele permite que o framework **execute uma função e injete
automaticamente seu retorno em uma rota**.

## Exemplo básico

``` python
from fastapi import FastAPI, Depends

app = FastAPI()

def get_message():
    return "Hello"

@app.get("/")
def route(msg: str = Depends(get_message)):
    return {"message": msg}
```

### Fluxo de execução

    Request
     ↓
    FastAPI executa dependency
     ↓
    Resultado é injetado no endpoint
     ↓
    Endpoint executa

------------------------------------------------------------------------

# 2. Dependências encadeadas

Dependências podem depender de **outras dependências**.

``` python
def get_repository():
    return Repository()

def get_usecase(repo = Depends(get_repository)):
    return UseCase(repo)

@app.get("/")
def route(usecase = Depends(get_usecase)):
    return usecase.execute()
```

### Fluxo

    Request
     ↓
    get_repository()
     ↓
    get_usecase()
     ↓
    endpoint

Isso permite criar **grafos de dependências automaticamente**.

------------------------------------------------------------------------

# 3. Factory

Uma **Factory** é uma função responsável por **criar objetos
manualmente**.

Diferente de `Depends`, a factory **não depende do FastAPI**.

## Exemplo

``` python
def controller_factory():
    repo = AgendaRepository()
    usecase = AgendaUseCase(repo)
    controller = AgendaController(usecase)

    return controller
```

### Uso

``` python
controller = controller_factory()

router.post("/agenda")(controller.create_agenda)
```

### Fluxo

    Aplicação inicia
     ↓
    Factory cria controller
     ↓
    Controller fica em memória
     ↓
    Requests usam o mesmo objeto

------------------------------------------------------------------------

# 4. Diferença entre Factory e Depends

  Característica           Factory         Depends
  ------------------------ --------------- -------------
  criação                  manual          automática
  controle                 desenvolvedor   FastAPI
  escopo comum             singleton       por request
  integração com FastAPI   baixa           alta

------------------------------------------------------------------------

# 5. Quando usar cada um

## Use Factory para

-   montar a estrutura da aplicação
-   criar controllers
-   criar use cases
-   criar repositories

### Fluxo

    Factory
     ↓
    Controller
     ↓
    UseCase
     ↓
    Repository

## Use Depends para

-   autenticação
-   sessão de banco
-   usuário logado
-   permissões
-   rate limit

### Fluxo

    Request
     ↓
    Depends executa
     ↓
    Endpoint

------------------------------------------------------------------------

# 6. Middleware

Middleware é uma função que **intercepta todas as requisições HTTP**.

Ele fica no **pipeline da aplicação**.

## Exemplo

``` python
from fastapi import Request

@app.middleware("http")
async def log_middleware(request: Request, call_next):

    print("ANTES DA ROTA")

    response = await call_next(request)

    print("DEPOIS DA ROTA")

    return response
```

### Fluxo

    Request
     ↓
    Middleware BEFORE
     ↓
    Router
     ↓
    Endpoint
     ↓
    Middleware AFTER
     ↓
    Response

------------------------------------------------------------------------

# 7. Quando usar Middleware

Use middleware para **tarefas globais de infraestrutura**.

Exemplos:

-   logging
-   métricas
-   tracing
-   manipulação de headers
-   CORS
-   compressão

Middleware afeta **toda a aplicação**.

------------------------------------------------------------------------

# 8. Hooks no FastAPI

No FastAPI, **hooks geralmente são implementados através de
dependencies**.

Eles permitem executar lógica **antes e depois da rota**.

## Exemplo

``` python
from fastapi import Depends, HTTPException

async def auth_guard():

    user = get_user()

    if not user:
        raise HTTPException(status_code=401)

    yield user
```

### Uso

``` python
@router.get("/")
async def route(user = Depends(auth_guard)):
    return {"user": user}
```

### Fluxo

    Request
     ↓
    auth_guard BEFORE
     ↓
    endpoint
     ↓
    auth_guard AFTER

------------------------------------------------------------------------

# 9. O papel do `yield`

`yield` divide uma dependency em **duas fases**:

-   antes do endpoint
-   depois do endpoint

## Exemplo

``` python
async def db_session():

    db = create_session()

    yield db

    db.close()
```

### Fluxo

    Request
     ↓
    Cria sessão
     ↓
    Endpoint executa
     ↓
    Fecha sessão

Isso permite **gerenciar recursos automaticamente**.

------------------------------------------------------------------------

# 10. `await call_next(request)`

`call_next` é usado **apenas em middleware**.

Ele continua o **fluxo da requisição**.

## Exemplo

``` python
@app.middleware("http")
async def middleware(request, call_next):

    print("before")

    response = await call_next(request)

    print("after")

    return response
```

### Fluxo

    Request
     ↓
    middleware BEFORE
     ↓
    call_next
     ↓
    router
     ↓
    endpoint
     ↓
    middleware AFTER
     ↓
    response

------------------------------------------------------------------------

# 11. Diferença entre `yield` e `call_next`

  Característica   `yield`                   `call_next`
  ---------------- ------------------------- ---------------
  usado em         dependency                middleware
  escopo           rota                      global
  controla         lifecycle da dependency   pipeline HTTP
  before/after     sim                       sim

------------------------------------------------------------------------

# 12. Regra mental simples

    Factory   → estrutura da aplicação
    Depends   → dependências da request
    Middleware → intercepta HTTP
    yield     → before/after de dependency
    call_next → continua pipeline HTTP

------------------------------------------------------------------------

# 13. Arquitetura comum no FastAPI

    Factory
     ↓
    Controller
     ↓
    UseCase
     ↓
    Endpoint
     ↓
    Depends (auth, db)
     ↓
    Middleware (logging, metrics)

------------------------------------------------------------------------

# 14. Conclusão

O FastAPI oferece vários mecanismos para controlar execução e
dependências:

-   **Factory** monta a estrutura da aplicação
-   **Depends** injeta dependências automaticamente
-   **Middleware** intercepta o pipeline HTTP
-   **Hooks (dependencies)** executam lógica antes/depois das rotas
-   **yield** controla o ciclo de vida de recursos
-   **call_next** continua o fluxo da requisição

Combinando esses elementos é possível construir **arquiteturas
escaláveis e organizadas**.

------------------------------------------------------------------------

🚨 **Perguntas de autoquestionamento (prioridade máxima)**

1.  **Estou investindo mais tempo em me preparar para agir do que agindo
    de fato?**
2.  **Quando peço uma correção ou explicação, estou aprendendo a fazer
    sozinho ou só terceirizando esse papel?**
3.  **Minhas decisões técnicas levam em conta o impacto
    humano/experiencial do que estou desenvolvendo?**
