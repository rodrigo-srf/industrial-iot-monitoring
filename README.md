# Monitoramento Industrial com MQTT

Projeto demonstrativo de **Automação Industrial, IIoT e DevOps** para monitorar máquinas em tempo real. Um simulador publica temperatura, vibração, corrente elétrica e rotação via MQTT; a aplicação Python registra as medições, identifica condições anormais e disponibiliza API, dashboard e observabilidade com Prometheus e Grafana.

> O projeto usa dados simulados e não deve ser empregado como sistema de segurança ou controle de uma planta real.

## Visão geral

```mermaid
flowchart LR
    A[Máquinas simuladas] -->|MQTT| B[Eclipse Mosquitto]
    B --> C[Coletor Python]
    C --> D[(PostgreSQL)]
    C --> E[Regras de alarme]
    D --> F[FastAPI]
    E --> F
    F --> G[Dashboard web]
    F --> H[/metrics]
    H --> I[Prometheus]
    I --> J[Grafana]
```

## Recursos

- telemetria de múltiplas máquinas via MQTT;
- temperatura, vibração, corrente e RPM;
- armazenamento histórico em PostgreSQL;
- regras de alarme para advertência e estado crítico;
- API REST com FastAPI e Swagger;
- dashboard web;
- métricas HTTP no formato Prometheus;
- monitoramento de taxa de requisições, latência, memória e respostas HTTP;
- dashboard Grafana provisionado automaticamente;
- ambiente completo com Docker Compose;
- execução do container com usuário não privilegiado;
- health checks;
- testes automatizados com Pytest;
- CI com lint, coverage, auditoria de dependências, scan de container e teste integrado da stack.

## Tecnologias

**Aplicação:** Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, MQTT e Eclipse Mosquitto  
**DevOps:** Docker, Docker Compose, GitHub Actions, Prometheus, Grafana e Trivy  
**Qualidade:** Pytest, pytest-cov, Ruff e pip-audit

## Como executar

Pré-requisito: Docker Desktop ou Docker Engine com Compose.

```bash
docker compose up --build
```

Depois, acesse:

- Dashboard industrial: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health
- Métricas Prometheus: http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Credenciais locais do Grafana:

```text
usuário: admin
senha: admin
```

Essas credenciais existem apenas para o laboratório local. Em produção, devem ser substituídas por secrets e autenticação apropriada.

O simulador inicia automaticamente e publica dados de três máquinas a cada dois segundos.

## Observabilidade

O FastAPI expõe métricas próprias em `/metrics`, incluindo:

- `industrial_http_requests_total`;
- `industrial_http_request_duration_seconds`;
- métricas padrão de processo e runtime do cliente Prometheus.

O Prometheus coleta essas métricas a cada cinco segundos e o Grafana carrega automaticamente o dashboard **Industrial Monitoring - Observability**.

A stack permite visualizar, entre outros indicadores:

- taxa de requisições HTTP;
- latência p95;
- uso de memória do processo;
- volume de respostas por status HTTP.

## CI/CD e validações

A pipeline do GitHub Actions executa:

```text
compile
  ↓
lint
  ↓
pytest + coverage
  ↓
pip-audit
  ↓
docker compose config
  ↓
docker build
  ↓
Trivy scan
  ↓
docker compose up
  ↓
API smoke test
  ↓
Prometheus target check
  ↓
Grafana health check
```

Assim, a CI valida não apenas o código Python, mas também se a stack completa consegue subir e se os componentes de observabilidade conseguem se comunicar.

## Principais endpoints

| Método | Rota | Finalidade |
|---|---|---|
| `GET` | `/api/health` | Verifica API, banco e estado MQTT |
| `GET` | `/api/machines` | Lista máquinas e sua última medição |
| `GET` | `/api/measurements/{machine_id}` | Retorna o histórico da máquina |
| `GET` | `/api/alarms` | Lista ocorrências de alarme recentes |
| `POST` | `/api/measurements` | Permite inserir telemetria sem MQTT |
| `GET` | `/metrics` | Expõe métricas para Prometheus |

## Tópico e formato MQTT

Tópico:

```text
factory/machines/{machine_id}/telemetry
```

Exemplo:

```json
{
  "machine_id": "MOTOR-01",
  "temperature_c": 67.4,
  "vibration_mm_s": 2.8,
  "current_a": 11.2,
  "rpm": 1760,
  "timestamp": "2026-09-20T14:30:00Z"
}
```

## Regras de alarme demonstrativas

| Variável | Advertência | Crítico |
|---|---:|---:|
| Temperatura | 75 °C | 90 °C |
| Vibração | 4,5 mm/s | 7,1 mm/s |
| Corrente | 14 A | 18 A |
| Rotação | abaixo de 1.500 RPM | abaixo de 1.200 RPM |

Os limites são ilustrativos. Em uma aplicação real, devem ser definidos com base no equipamento, processo, normas aplicáveis e análise de risco.

## Testes locais

Sem Docker:

```bash
pip install -r requirements.txt
pytest -q
```

Validação do Compose:

```bash
docker compose config
```

Encerrar toda a stack:

```bash
docker compose down -v
```

## Possíveis evoluções

- integração com ESP32 e sensores reais;
- autenticação e perfis de acesso;
- manutenção preditiva com séries temporais;
- alertas do Prometheus com Alertmanager;
- protocolo Modbus TCP para comunicação com CLPs;
- infraestrutura como código com Terraform.

## Autor

**Rodrigo Serafim** — Automação Industrial, Python Backend, IoT e Engenharia Elétrica.

- GitHub: [rodrigo-srf](https://github.com/rodrigo-srf)
- LinkedIn: [Rodrigo Serafim](https://www.linkedin.com/in/rodrigo-srf/)
