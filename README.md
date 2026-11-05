# Multi-Tenant Workforce Attendance & Dining AI SaaS

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16%20RLS-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![React Native Expo](https://img.shields.io/badge/Expo-SDK%2058-000020.svg?style=flat&logo=expo&logoColor=white)](https://expo.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Playwright](https://img.shields.io/badge/Playwright-E2E%20Tested-2EAD33.svg?style=flat&logo=playwright&logoColor=white)](https://playwright.dev)
[![Pytest](https://img.shields.io/badge/Pytest-30%2F30%20Passing-0A9EDC.svg?style=flat&logo=pytest&logoColor=white)](https://pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade, multi-tenant enterprise SaaS portfolio platform engineered for workforce management, real-time dining hall (*comedor industrial*) badge tracking, and AI-assisted meal demand forecasting.

Built with **Hexagonal Architecture (Ports & Adapters)**, **Tactical Domain-Driven Design (DDD)**, **PostgreSQL Row-Level Security (RLS)** for strict data isolation, and a **React Native (Expo)** cross-platform mobile and web client.

---

## 🏛️ Architecture & Engineering Principles

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                               │
│   FastAPI Single-Action Controllers  │  Multi-Tenant WebSocket Handlers  │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      │ Invokes (DTOs / Commands)
┌─────────────────────────────────────▼────────────────────────────────────┐
│                         APPLICATION LAYER                                │
│        Use Cases (Input / Output Ports, Orchestration, Outbox)           │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      │ Coordinates
┌─────────────────────────────────────▼────────────────────────────────────┐
│                           DOMAIN LAYER                                   │
│  Aggregate Roots  │  Domain Events  │  Value Objects  │  Domain Invariants│
└─────────────────────────────────────▲────────────────────────────────────┘
                                      │ Implements Ports
┌─────────────────────────────────────┴────────────────────────────────────┐
│                      INFRASTRUCTURE LAYER                                │
│   PostgreSQL RLS Sessions  │  SQLAlchemy Repositories  │  Event Bus      │
│   Idempotency Middleware   │  Real-Time Tenant Rooms   │  Secure Storage │
└──────────────────────────────────────────────────────────────────────────┘
```

### 1. Tactical Domain-Driven Design (DDD)
- **Aggregate Roots**: `Tenant`, `User`, `Employee`, `MealRecord` encapsulate business rules, state changes, and consistency boundaries.
- **Value Objects**: Self-validating immutable types (`Email`, `BadgeCode`, `TenantSlug`, `DocumentId`, `FullName`, `MealType`) enforcing domain invariants upon instantiation.
- **Domain Events**: Aggregates record domain events (`TenantRegistered`, `EmployeeCreated`, `MealBadgeScanned`, `MealRecorded`) published via an asynchronous `EventBus` to decouple cross-context side effects.
- **Object Mothers & Test Doubles**: Unit testing suite follows CodelyTV patterns with dedicated Object Mothers (`TenantMother`, `EmployeeMother`, `MealRecordMother`) and strict behavioral assertions.

### 2. Multi-Tenancy via PostgreSQL Row-Level Security (RLS)
Unlike naive logical tenant filters (`WHERE tenant_id = x`), this platform relies on PostgreSQL native Row-Level Security policies:
- Database connections execute `SELECT set_config('app.current_tenant_id', :tenant_id, true)` in a local transaction context.
- Tables (`tenants`, `users`, `employees`, `meal_records`) apply row-level security policies (`USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)`).
- Cross-tenant data leakage is fundamentally prevented at the database engine level, even against arbitrary raw SQL queries.

### 3. Single-Action Controllers (Action-Domain-Responder)
Every HTTP endpoint is isolated into its own dedicated Single-Action Controller class with a single static `handle` method. This eliminates monolithic controller bloat and adheres strictly to the Single Responsibility Principle (SRP).

### 4. Distributed Idempotency (`X-Idempotency-Key`)
- Mutation endpoints (`POST /api/v1/dining/scan`, `POST /api/v1/workforce/employees`) support the `X-Idempotency-Key` HTTP header.
- The `IdempotencyMiddleware` intercepts requests, records in-flight keys to eliminate race conditions, and caches responses.
- Replayed requests return cached payloads immediately with the `X-Cache-Lookup: HIT-IDEMPOTENT` response header, preventing duplicate transactions from network retries or rapid button clicks.

### 5. Multi-Tenant Real-Time WebSocket Engine
- WebSocket endpoints authenticate clients via JWT and assign connections into tenant-isolated rooms (`TenantConnectionManager`).
- When a meal scan aggregate fires a `MealRecordedDomainEvent`, domain subscribers broadcast the payload exclusively to active terminals sharing the identical `tenant_id`.

### 6. Heuristic AI Meal Demand Forecasting
- The `HeuristicAiDiningPredictor` analyzes historical shift attendance, active departmental headcount ratios, and meal service windows.
- Outputs recommended food preparation quotas in kilograms, predicted attendance volumes, and operational confidence scores to minimize industrial food waste and overproduction.

---

## 💻 Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.14)
- **Database Engine**: [PostgreSQL 16](https://www.postgresql.org/) with Row-Level Security (RLS)
- **ORM & Driver**: [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/) + [asyncpg](https://github.com/MagicStack/asyncpg)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Validation & Typing**: [Pydantic v2](https://docs.pydantic.dev/) + `email-validator`
- **Security**: [bcrypt](https://pypi.org/project/bcrypt/) password hashing + [PyJWT](https://pyjwt.readthedocs.io/)
- **Testing**: [Pytest](https://pytest.org/) with `pytest-asyncio` (30/30 unit, acceptance, and e2e tests)

### Frontend
- **Framework**: [React Native](https://reactnative.dev/) with [Expo SDK 58](https://expo.dev/) (React 19 + TypeScript 5.9)
- **Web Support**: Expo Web (`react-native-web`, `@expo/metro-runtime`)
- **State Management**: [Zustand](https://github.com/pmndrs/zustand) with cross-platform secure storage
- **Server Cache & Sync**: [TanStack Query v5](https://tanstack.com/query)
- **Forms & Validation**: [React Hook Form](https://react-hook-form.com/) + [Zod](https://zod.dev/)
- **List Optimization**: Virtualized `FlatList` with `React.memo` and extracted render items
- **E2E Testing**: [Playwright](https://playwright.dev/) running automated cross-browser flows in Chromium

---

## 📁 Project Structure

```
├── .env.example                     # Environment template (zero committed secrets)
├── docker-compose.yml               # PostgreSQL 16 + FastAPI service orchestration
│
├── backend/
│   ├── alembic/                     # Database migrations with RLS policies
│   ├── src/
│   │   ├── shared/                  # Cross-cutting domain & infrastructure
│   │   │   ├── domain/              # AggregateRoot, ValueObject, DomainEvent, EventBus
│   │   │   └── infrastructure/      # DB session, TenantContext, Idempotency, Realtime WS
│   │   │
│   │   └── contexts/                # Bounded Contexts (Package by Feature)
│   │       ├── iam/                 # Identity & Access Management (Tenant Onboarding & JWT)
│   │       │   ├── domain/          # Tenant & User Aggregates
│   │       │   ├── application/     # RegisterTenantUseCase, LoginUseCase
│   │       │   ├── infrastructure/  # SQLAlchemy Repositories & Password Hasher
│   │       │   └── presentation/    # Single-Action Controllers & Routes
│   │       │
│   │       ├── workforce/           # Employee Management
│   │       │   ├── domain/          # Employee Aggregate Root & Document VO
│   │       │   ├── application/     # Create, List, Detail, Update, Delete Use Cases
│   │       │   ├── infrastructure/  # SQLAlchemy Employee Repository
│   │       │   └── presentation/    # Single-Action CRUD Controllers
│   │       │
│   │       └── dining/              # Dining Hall Tracking & AI Forecasting
│   │           ├── domain/          # MealRecord Aggregate & MealRecordedDomainEvent
│   │           ├── application/     # ScanBadgeUseCase, MetricsUseCase, ForecastUseCase
│   │           ├── infrastructure/  # SQLAlchemy Repositories, Event Subscribers, AI Predictor
│   │           └── presentation/    # ScanMealBadgeController, WebSocket Controller
│   │
│   └── tests/
│       ├── unit/                    # Domain Aggregate & Use Case unit tests with Object Mothers
│       ├── acceptance/              # BDD Given-When-Then acceptance tests
│       └── e2e/                     # HTTP API lifecycle, Idempotency replay, & WebSocket isolation
│
└── frontend/
    ├── e2e/                         # Playwright automated browser test specs
    ├── src/
    │   ├── shared/                  # ApiClient, cross-platform SecureStorage, UI Components
    │   └── features/
    │       ├── auth/                # Zustand AuthStore, Zod schemas, LoginForm, RegisterForm
    │       ├── employees/           # EmployeeList (FlatList), Modals, TanStack Query hooks
    │       └── dining/              # QR Scanner Terminal, Live WS Hook, AI Forecast Panel
    └── App.tsx                      # Root component with Tab Navigation & Session Hydration
```

---

## 🔒 Security & Privacy Model

- **Zero Committed Secrets**: `.env` is ignored by default; all credentials and tokens are injected via environment variables.
- **Row-Level Security**: Every SQL query is automatically constrained to the authenticated `tenant_id` at the database kernel.
- **Cross-Platform Secure Storage**: Tokens are stored in hardware-backed `expo-secure-store` (Keychain on iOS, EncryptedSharedPreferences on Android) with a fallback adapter for Web environments.
- **Double-Submit Prevention**: Mutation buttons automatically generate UUID v4 idempotency keys, disabling UI elements during in-flight mutations.

---

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (v3.12+ for local virtualenv development)

---

### 1. Backend Setup with Docker Compose

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/workforce-dining-saas.git
   cd workforce-dining-saas
   ```

2. Copy the environment variables:
   ```bash
   cp .env.example .env
   ```

3. Spin up the PostgreSQL and FastAPI containers:
   ```bash
   docker compose up -d --build
   ```

4. Verify service health:
   - PostgreSQL is running on host port `5435`
   - FastAPI is running on `http://localhost:8001`
   - Swagger Interactive Documentation: [http://localhost:8001/docs](http://localhost:8001/docs)

5. Run database migrations:
   ```bash
   docker compose exec backend alembic upgrade head
   ```

---

### 2. Frontend Setup (Expo Web & Mobile)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   ```

2. Copy frontend environment variables:
   ```bash
   cp .env.example .env
   ```

3. Start Expo in Web mode:
   ```bash
   npx expo start --web --port 8081
   ```

4. Open [http://localhost:8081](http://localhost:8081) in your browser.

---

## 🧪 Testing

### Backend Test Suite (Pytest)
The backend includes 30 automated tests spanning pure domain unit tests, acceptance tests (ATDD), and end-to-end integration tests:

```bash
cd backend
# With local virtual environment activated:
pytest tests/ -v
```

```
============================= test session starts =============================
collected 30 items

tests/acceptance/test_dining_acceptance.py .                             [  3%]
tests/acceptance/test_iam_acceptance.py ..                               [ 10%]
tests/acceptance/test_workforce_acceptance.py ..                         [ 16%]
tests/e2e/test_api_e2e.py .                                              [ 20%]
tests/e2e/test_idempotency_e2e.py .                                      [ 23%]
tests/e2e/test_websocket_multitenant_e2e.py ..                           [ 30%]
tests/unit/application/test_create_employee_use_case_unit.py ..          [ 36%]
tests/unit/application/test_forecast_dining_demand_use_case_unit.py .    [ 40%]
tests/unit/application/test_register_tenant_use_case_unit.py ..          [ 46%]
tests/unit/application/test_scan_meal_badge_use_case_unit.py ...         [ 56%]
tests/unit/application/test_update_employee_use_case_unit.py ..          [ 63%]
tests/unit/domain/test_employee_aggregate_unit.py ...                    [ 73%]
tests/unit/domain/test_meal_record_aggregate_unit.py ..                  [ 80%]
tests/unit/domain/test_tenant_aggregate_unit.py ..                       [ 86%]
tests/unit/domain/test_value_objects_unit.py ....                        [100%]

======================== 30 passed in 1.90s ========================
```

---

### Frontend E2E Test Suite (Playwright)
Validates reactive form validation, multi-tenant onboarding, employee creation, virtualized list rendering, real-time WebSocket connectivity, and duplicate scan blocking in a headless Chromium browser:

```bash
cd frontend
npx playwright test
```

```
Running 4 tests using 4 workers

  ✓  [chromium] › should render login screen with form inputs and buttons (964ms)
  ✓  [chromium] › should show validation errors when submitting empty form (1.1s)
  ✓  [chromium] › should toggle between Login and Register Tenant forms (1.1s)
  ✓  [chromium] › should complete full tenant onboarding, employee registration, and dining scan flow (2.3s)

  4 passed (12.6s)
```

---

## 📡 API Specification Summary

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register-tenant` | Onboard new organization tenant and admin user | No |
| `POST` | `/api/v1/auth/login` | Authenticate tenant user and issue JWT | No |
| `GET` | `/api/v1/workforce/employees` | List active employees for authenticated tenant (RLS) | Yes |
| `POST` | `/api/v1/workforce/employees` | Register new employee (`X-Idempotency-Key` supported) | Yes |
| `GET` | `/api/v1/workforce/employees/{id}` | Retrieve employee detail | Yes |
| `PUT` | `/api/v1/workforce/employees/{id}` | Update employee profile | Yes |
| `DELETE` | `/api/v1/workforce/employees/{id}` | Soft-delete / deactivate employee | Yes |
| `POST` | `/api/v1/dining/scan` | Scan employee badge for lunch/meal quota with duplicate detection | Yes |
| `GET` | `/api/v1/dining/metrics/today` | Real-time aggregate count of meals served today | Yes |
| `GET` | `/api/v1/dining/ai/forecast` | Heuristic AI lunch attendance and portion demand forecast | Yes |
| `WS` | `/api/v1/dining/ws?token={jwt}` | Multi-tenant real-time WebSocket connection | Query Token |

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
