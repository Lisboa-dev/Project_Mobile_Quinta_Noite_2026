# Interfaces e Classes Abstratas em Python

## 📌 Introdução

Em Python, não existe uma palavra-chave explícita chamada `interface` como em linguagens como Java ou C#. No entanto, é possível **simular interfaces** e também criar **classes abstratas** utilizando o módulo padrão `abc` (Abstract Base Classes).

Esses conceitos são fundamentais para:

* Definir contratos de comportamento
* Garantir consistência entre implementações
* Facilitar manutenção e escalabilidade

---

## 🧱 Classes Abstratas

Uma **classe abstrata** é uma classe que não pode ser instanciada diretamente e serve como base para outras classes.

### 🔧 Como criar uma classe abstrata

```python
from abc import ABC, abstractmethod

class Animal(ABC):

    @abstractmethod
    def emitir_som(self):
        pass
```

### 📌 Explicação

* `ABC`: classe base para definir classes abstratas
* `@abstractmethod`: define um método que deve ser implementado pelas subclasses
* Não é possível instanciar `Animal`

```python
animal = Animal()  # ❌ Erro
```

---

## 🐶 Implementando uma Classe Concreta

```python
class Cachorro(Animal):

    def emitir_som(self):
        return "Latido"

c = Cachorro()
print(c.emitir_som())  # Latido
```

### 📌 Regra importante

Toda classe que herda de uma classe abstrata **deve implementar todos os métodos abstratos**, ou também será abstrata.

---

## 📐 Interfaces em Python (Forma Simulada)

Python usa tipagem dinâmica, então interfaces são geralmente simuladas de duas formas:

### 1. Usando Classes Abstratas

```python
class Pagamento(ABC):

    @abstractmethod
    def pagar(self, valor):
        pass
```

```python
class CartaoCredito(Pagamento):

    def pagar(self, valor):
        print(f"Pagando {valor} no cartão")
```

---

### 2. Duck Typing (Tipagem Implícita)

Python também permite usar objetos sem herança explícita, desde que implementem os métodos esperados.

```python
class Boleto:
    def pagar(self, valor):
        print(f"Pagando {valor} com boleto")


def processar_pagamento(pagamento):
    pagamento.pagar(100)
```

```python
b = Boleto()
processar_pagamento(b)
```

### 📌 Conceito

> "Se anda como um pato e faz quack como um pato, então é um pato"

---

## ⚖️ Interface vs Classe Abstrata

| Característica        | Classe Abstrata  | Interface (simulada) |
| --------------------- | ---------------- | -------------------- |
| Implementação parcial | ✅ Sim            | ❌ Geralmente não     |
| Métodos concretos     | ✅ Pode ter       | ❌ Evita-se           |
| Herança               | Simples (Python) | Simples              |
| Objetivo              | Reuso + contrato | Apenas contrato      |

---

## 🧠 Boas Práticas

* Use classes abstratas quando houver **comportamento comum**
* Use interfaces (via ABC) quando quiser **forçar contratos**
* Prefira composição quando possível
* Evite heranças profundas

---

## 🚀 Exemplo Completo

```python
from abc import ABC, abstractmethod

class Forma(ABC):

    @abstractmethod
    def area(self):
        pass

class Quadrado(Forma):

    def __init__(self, lado):
        self.lado = lado

    def area(self):
        return self.lado ** 2

class Circulo(Forma):

    def __init__(self, raio):
        self.raio = raio

    def area(self):
        return 3.14 * self.raio ** 2

formas = [Quadrado(2), Circulo(3)]

for f in formas:
    print(f.area())
```

---

## 🧬 Interfaces modernas com Protocol (typing)

A partir do Python 3.8+, podemos usar `Protocol` do módulo `typing` (ou `typing_extensions`) para definir **interfaces reais baseadas em tipagem estrutural**.

Isso é muito mais próximo do conceito formal de interface.

---

### 🔧 Criando uma interface com Protocol

```python
from typing import Protocol

class Pagamento(Protocol):
    def pagar(self, valor: float) -> None:
        ...
```

### 📌 Explicação

* `Protocol` define um **contrato estrutural**
* Não é necessário herdar explicitamente da interface
* Qualquer classe que implemente os métodos esperados será aceita

---

### 🧪 Implementação sem herança explícita

```python
class Pix:
    def pagar(self, valor: float) -> None:
        print(f"Pagando {valor} via Pix")

class Cartao:
    def pagar(self, valor: float) -> None:
        print(f"Pagando {valor} no cartão")
```

```python
def processar_pagamento(p: Pagamento):
    p.pagar(100)

processar_pagamento(Pix())
processar_pagamento(Cartao())
```

### 💡 Importante

Mesmo sem herdar de `Pagamento`, as classes funcionam porque seguem o contrato.

---

### ⚖️ Protocol vs ABC

| Característica      | ABC (Abstract Base Class) | Protocol         |
| ------------------- | ------------------------- | ---------------- |
| Tipo de verificação | Nominal (herança)         | Estrutural       |
| Precisa herdar?     | ✅ Sim                     | ❌ Não            |
| Flexibilidade       | Média                     | Alta             |
| Uso comum           | Regras rígidas            | Tipagem flexível |

---

### 🧠 Quando usar Protocol?

Use `Protocol` quando:

* Você quer **baixo acoplamento**
* Não controla todas as implementações
* Quer aproveitar duck typing com segurança
* Está trabalhando com tipagem estática (mypy, pyright)

---

### 🚀 Exemplo mais avançado

```python
from typing import Protocol

class Repositorio(Protocol):
    def salvar(self, dado: dict) -> None: ...
    def listar(self) -> list[dict]: ...

class RepositorioMemoria:
    def __init__(self):
        self._dados = []

    def salvar(self, dado: dict) -> None:
        self._dados.append(dado)

    def listar(self) -> list[dict]:
        return self._dados


def usar_repo(repo: Repositorio):
    repo.salvar({"id": 1})
    print(repo.listar())

usar_repo(RepositorioMemoria())
```

---

## 🎯 Conclusão

* Python não possui interfaces nativas, mas o módulo `abc` resolve isso bem
* Classes abstratas ajudam a estruturar sistemas grandes
* Duck typing é poderoso, mas deve ser usado com responsabilidade

---

