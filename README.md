#  Transaction Authorization Engine — FastAPI & Clean Architecture

Microserviço de autorização e liquidação de transações financeiras com foco em concorrência, idempotência e integridade transacional.

---

##  Visão Geral
Simulador de core banking para processamento de débitos e créditos em contas correntes, garantindo consistência ACID, validação de saldos e controle de idempotência para mitigar requisições duplicadas (*double-spending*).

---

##  Tecnologias & Padrões
* **Linguagem & Framework**: Python 3.12 / FastAPI
* **Banco de Dados**: PostgreSQL + SQLAlchemy (Async)
* **Controle de Idempotência**: Redis (Locks distribuídos / Idempotency-Key)
* **Testes & Qualidade**: Pytest (Unitários e Integração), Black, Flake8
* **Containerização**: Docker & Docker Compose

---

##  Padrões de Arquitetura
* **Domain-Driven Design (DDD) & Clean Architecture**: Separação clara entre Domínio, Casos de Uso (Application) e Infraestrutura.
* **Controle de Concorrência**: Tratamento de consistência em atualizações de saldo na camada de banco de dados.
* **Middlewares de Logging Estruturado**: Rastreabilidade com `correlation-id` em cada ciclo de requisição.

---

##  Endpoints Principais

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/v1/accounts` | Criação de conta corrente |
| `GET` | `/api/v1/accounts/{id}/balance` | Consulta de saldo atual |
| `POST` | `/api/v1/transactions/authorize` | Autorização de débito/transferência (Requer `Idempotency-Key`) |

---

##  Como Rodar Localmente & Testes

### 1. Subir aplicação e banco via Docker
```bash
docker-compose up --build -d
