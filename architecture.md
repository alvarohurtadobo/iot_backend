# Arquitectura del Sistema - IoT Monitor

**Versión:** 1.0  
**Última actualización:** 2024

---

## 📋 Tabla de Contenidos

- [Arquitectura Actual](#arquitectura-actual)
- [Capas del Sistema](#capas-del-sistema)
- [Mapeo a Clean Architecture](#mapeo-a-clean-architecture)
- [Analogía con Modelo OSI](#analogía-con-modelo-osi)
- [Flujo de Datos](#flujo-de-datos)
- [Evoluciones Futuras](#evoluciones-futuras)
- [Decisiones de Diseño](#decisiones-de-diseño)

---

## Arquitectura Actual

### Visión General

El sistema IoT Monitor sigue una arquitectura en capas (Layered Architecture) con separación clara de responsabilidades. La aplicación está estructurada en módulos que se comunican a través de interfaces bien definidas.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Routers    │  │   Schemas    │  │ Dependencies │      │
│  │  (FastAPI)   │  │  (Pydantic)  │  │   (Auth)     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼─────────────┘
          │                 │                 │
┌─────────┼─────────────────┼─────────────────┼─────────────┐
│                    APPLICATION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Services   │  │  IoT Services│  │  Validators  │    │
│  │ (Business)   │  │  (TimeData)  │  │  (Security)  │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
└─────────┼─────────────────┼─────────────────┼─────────────┘
          │                 │                 │
┌─────────┼─────────────────┼─────────────────┼─────────────┐
│                      DOMAIN LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Models     │  │  Entities    │  │  Enums       │    │
│  │ (SQLAlchemy) │  │  (Business)  │  │  (States)    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
└─────────┼─────────────────┼─────────────────┼─────────────┘
          │                 │                 │
┌─────────┼─────────────────┼─────────────────┼─────────────┐
│                  INFRASTRUCTURE LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Database    │  │  MQTT Client │  │   Config     │    │
│  │ (PostgreSQL) │  │  (paho-mqtt) │  │  (Settings)  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Capas del Sistema

### 1. Presentation Layer (Capa de Presentación)

**Ubicación:** `app/api/`

**Responsabilidades:**
- Manejo de requests HTTP
- Validación de entrada (Pydantic schemas)
- Serialización de respuestas
- Manejo de errores HTTP
- Autenticación y autorización

**Componentes:**

```
app/api/
├── routers/          # Endpoints HTTP (FastAPI routers)
│   ├── auth.py      # Autenticación
│   ├── users.py     # Gestión de usuarios
│   └── roles.py     # Gestión de roles
├── schemas/          # DTOs (Data Transfer Objects)
│   ├── auth.py      # Schemas de autenticación
│   ├── users.py     # Schemas de usuarios
│   └── roles.py     # Schemas de roles
└── dependencies/     # Dependencias de FastAPI
    └── auth.py      # get_current_user, etc.
```

**Características:**
- **Stateless**: No mantiene estado entre requests
- **Thin Layer**: Lógica mínima, delega a servicios
- **Validation**: Pydantic valida automáticamente
- **Documentation**: Swagger/OpenAPI automático

---

### 2. Application Layer (Capa de Aplicación)

**Ubicación:** `app/services/`, `app/iot_data/`

**Responsabilidades:**
- Lógica de negocio
- Orquestación de operaciones
- Validaciones de negocio
- Transformación de datos entre capas

**Componentes:**

```
app/services/
├── users.py         # Lógica de negocio de usuarios
└── roles.py         # Lógica de negocio de roles

app/iot_data/
├── service.py       # Servicio de datos IoT (en memoria)
└── time_data_service.py  # Servicio de TimeData (DB)
```

**Estado Actual:**
- **Usuarios y Roles**: Almacenamiento en memoria (temporal)
- **IoT Data**: Acceso directo a base de datos
- **Nota**: Los servicios de usuarios/roles deberían migrar a DB

**Características:**
- **Business Logic**: Contiene reglas de negocio
- **Transaction Management**: Maneja transacciones de DB
- **Error Handling**: Convierte excepciones de dominio a HTTP

---

### 3. Domain Layer (Capa de Dominio)

**Ubicación:** `app/db/models/`, `app/iot_data/schemas.py`

**Responsabilidades:**
- Entidades del dominio
- Modelos de datos
- Enums y tipos de dominio
- Relaciones entre entidades

**Componentes:**

```
app/db/models/
├── user.py          # Entidad Usuario
├── role.py          # Entidad Rol
├── device.py        # Entidad Dispositivo
├── sensor.py        # Entidad Sensor
├── time_data.py     # Entidad TimeData
├── business.py      # Entidad Empresa
├── branch.py        # Entidad Sucursal
├── machine.py       # Entidad Máquina
└── ...              # Otras entidades

app/iot_data/schemas.py
└── DeviceState      # Enum de estados
```

**Características:**
- **Rich Domain Models**: Contienen lógica de dominio cuando es apropiado
- **ORM Mapping**: SQLAlchemy mapea a tablas de DB
- **Relationships**: Define relaciones entre entidades
- **Validation**: Validaciones a nivel de modelo

---

### 4. Infrastructure Layer (Capa de Infraestructura)

**Ubicación:** `app/db/`, `app/mqtt/`, `app/core/`

**Responsabilidades:**
- Acceso a datos (PostgreSQL)
- Comunicación externa (MQTT)
- Configuración del sistema
- Utilidades de infraestructura

**Componentes:**

```
app/db/
├── base.py          # Configuración SQLAlchemy
└── models/          # Modelos ORM

app/mqtt/
├── client.py        # Cliente MQTT (paho-mqtt)
└── schemas.py       # Schemas de mensajes MQTT

app/core/
├── config.py        # Configuración (Pydantic Settings)
├── security.py      # JWT, hashing, validación
└── rate_limit.py    # Rate limiting
```

**Características:**
- **External Dependencies**: Interfaz con sistemas externos
- **Configuration**: Gestión de configuración
- **Cross-cutting Concerns**: Seguridad, logging, etc.

---

## Mapeo a Clean Architecture

### Principios de Clean Architecture

El proyecto actual sigue parcialmente los principios de Clean Architecture, con oportunidades de mejora:

```
┌─────────────────────────────────────────────────────┐
│              PRESENTATION (Outer)                   │
│  ┌──────────────────────────────────────────────┐  │
│  │  Frameworks & Drivers                         │  │
│  │  - FastAPI Routers                            │  │
│  │  - Pydantic Schemas                           │  │
│  │  - HTTP Handlers                              │  │
│  └──────────────────────────────────────────────┘  │
│              ↓                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Interface Adapters                          │  │
│  │  - Services (Application Layer)               │  │
│  │  - DTOs (Data Transfer Objects)               │  │
│  └──────────────────────────────────────────────┘  │
│              ↓                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Application Business Rules                   │  │
│  │  - Use Cases                                  │  │
│  │  - Business Logic                             │  │
│  └──────────────────────────────────────────────┘  │
│              ↓                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Enterprise Business Rules (Inner)            │  │
│  │  - Domain Models                              │  │
│  │  - Entities                                   │  │
│  │  - Value Objects                              │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Mapeo Actual

| Clean Architecture | Implementación Actual | Estado |
|-------------------|----------------------|--------|
| **Frameworks & Drivers** | FastAPI, Pydantic, SQLAlchemy | ✅ Implementado |
| **Interface Adapters** | Services, Schemas | ⚠️ Parcial (algunos servicios en memoria) |
| **Application Business Rules** | Lógica en services | ⚠️ Mezclado con infraestructura |
| **Enterprise Business Rules** | Models, Entities | ✅ Implementado |

### Mejoras Necesarias para Clean Architecture

1. **Separar Use Cases:**
   ```
   app/use_cases/
   ├── user/
   │   ├── create_user.py
   │   ├── update_user.py
   │   └── delete_user.py
   └── iot/
       └── ingest_data.py
   ```

2. **Repository Pattern:**
   ```
   app/repositories/
   ├── user_repository.py
   └── time_data_repository.py
   ```

3. **Domain Services:**
   ```
   app/domain/
   ├── services/
   │   └── password_validator.py
   └── entities/
       └── user.py
   ```

---

## Analogía con Modelo OSI

Aunque el modelo OSI es para redes, podemos hacer una analogía con las capas de aplicación:

### Modelo OSI de Aplicación (7 Capas)

```
┌─────────────────────────────────────────────────────┐
│ 7. Application Layer  →  Presentation Layer        │
│    (HTTP, REST API)      (Routers, Schemas)        │
├─────────────────────────────────────────────────────┤
│ 6. Presentation Layer →  Application Layer          │
│    (Data Formatting)     (Services, Business Logic) │
├─────────────────────────────────────────────────────┤
│ 5. Session Layer     →   Domain Layer               │
│    (Session Management)  (Models, Entities)        │
├─────────────────────────────────────────────────────┤
│ 4. Transport Layer   →   Infrastructure Layer       │
│    (TCP/UDP)             (Database, MQTT)          │
├─────────────────────────────────────────────────────┤
│ 3. Network Layer    →   Network Infrastructure     │
│    (IP Routing)           (Docker, Networking)      │
├─────────────────────────────────────────────────────┤
│ 2. Data Link Layer  →   Container Layer            │
│    (Ethernet)             (Docker Networking)       │
├─────────────────────────────────────────────────────┤
│ 1. Physical Layer   →   Hardware Layer              │
│    (Cables, Signals)      (Servers, Storage)        │
└─────────────────────────────────────────────────────┘
```

### Mapeo Detallado

| Capa OSI | Función | Equivalente en Backend | Implementación |
|----------|---------|------------------------|----------------|
| **7. Application** | Interfaz de usuario/aplicación | Presentation Layer | FastAPI Routers |
| **6. Presentation** | Formato de datos, encriptación | Application Layer | Services, DTOs |
| **5. Session** | Gestión de sesiones | Domain Layer | Models, State |
| **4. Transport** | Confiabilidad de datos | Infrastructure | Database, MQTT |
| **3. Network** | Enrutamiento | Network | Docker Networking |
| **2. Data Link** | Acceso al medio | Container | Docker Bridge |
| **1. Physical** | Transmisión física | Hardware | Servidores |

---

## Flujo de Datos

### Flujo de Request HTTP

```
1. Cliente HTTP
   ↓
2. FastAPI Router (Presentation)
   ├── Validación con Pydantic Schema
   ├── Autenticación (Dependencies)
   └── Extracción de parámetros
   ↓
3. Service Layer (Application)
   ├── Validación de negocio
   ├── Lógica de negocio
   └── Orquestación
   ↓
4. Repository/Model (Domain)
   ├── Acceso a datos
   └── Mapeo ORM
   ↓
5. Database (Infrastructure)
   └── PostgreSQL
```

### Flujo de Datos MQTT

```
1. Dispositivo IoT
   ↓ (MQTT Message)
2. MQTT Broker
   ↓
3. MQTT Client (Infrastructure)
   ├── Recepción de mensaje
   └── Validación con Pydantic
   ↓
4. TimeData Service (Application)
   ├── Validación de negocio
   └── Transformación
   ↓
5. Database Model (Domain)
   └── Persistencia
   ↓
6. PostgreSQL (Infrastructure)
```

---

## Evoluciones Futuras

### Fase 1: Refactorización a Clean Architecture (v0.2.0)

#### 1.1 Implementar Repository Pattern

**Estructura Propuesta:**
```
app/
├── domain/
│   ├── entities/          # Entidades puras (sin ORM)
│   │   ├── user.py
│   │   └── device.py
│   ├── repositories/      # Interfaces (ABC)
│   │   ├── user_repository.py
│   │   └── time_data_repository.py
│   └── services/          # Domain services
│       └── password_validator.py
├── application/
│   ├── use_cases/         # Casos de uso
│   │   ├── user/
│   │   │   ├── create_user.py
│   │   │   ├── update_user.py
│   │   │   └── delete_user.py
│   │   └── iot/
│   │       └── ingest_data.py
│   └── dto/               # Data Transfer Objects
│       ├── user_dto.py
│       └── iot_dto.py
├── infrastructure/
│   ├── persistence/       # Implementación de repositorios
│   │   ├── user_repository_impl.py
│   │   └── time_data_repository_impl.py
│   ├── external/          # Servicios externos
│   │   └── mqtt_client.py
│   └── config/            # Configuración
└── presentation/
    ├── api/               # FastAPI
    │   ├── routers/
    │   └── schemas/
    └── mqtt/              # Handlers MQTT
```

**Beneficios:**
- Separación clara de responsabilidades
- Testabilidad mejorada (mocks fáciles)
- Independencia de frameworks
- Facilita cambios de infraestructura

---

### Fase 2: Arquitectura Hexagonal (v0.3.0)

#### 2.1 Ports and Adapters

```
                    ┌─────────────────┐
                    │   Application    │
                    │     Core         │
                    │                  │
                    │  ┌───────────┐   │
                    │  │  Ports    │   │
                    │  │ (Interfaces)│ │
                    │  └───────────┘   │
                    └────────┬──────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│ HTTP Adapter   │  │  MQTT Adapter   │  │  DB Adapter    │
│ (FastAPI)      │  │  (paho-mqtt)    │  │  (SQLAlchemy)  │
└────────────────┘  └─────────────────┘  └────────────────┘
```

**Implementación:**
- **Ports (Interfaces):**
  ```python
  # app/domain/ports/user_repository.py
  class UserRepository(ABC):
      @abstractmethod
      def find_by_id(self, user_id: UUID) -> User:
          pass
  ```

- **Adapters (Implementaciones):**
  ```python
  # app/infrastructure/adapters/user_repository_sqlalchemy.py
  class SQLAlchemyUserRepository(UserRepository):
      def find_by_id(self, user_id: UUID) -> User:
          # Implementación con SQLAlchemy
  ```

---

### Fase 3: Event-Driven Architecture (v0.4.0)

#### 3.1 Event Bus y Domain Events

```
┌─────────────┐
│   Domain    │
│  Entities   │
└──────┬──────┘
       │
       │ Domain Events
       │
┌──────▼──────────────────┐
│    Event Bus             │
│  (Pub/Sub Pattern)       │
└──────┬───────────────────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌──▼──┐
│Handler│ │Handler│
└──────┘ └──────┘
```

**Eventos Propuestos:**
- `UserCreated`
- `DeviceStateChanged`
- `DataIngested`
- `AlertTriggered`

**Implementación:**
```python
# app/domain/events/user_created.py
@dataclass
class UserCreated(DomainEvent):
    user_id: UUID
    email: str
    timestamp: datetime

# app/application/handlers/user_created_handler.py
class UserCreatedHandler:
    def handle(self, event: UserCreated):
        # Enviar email de bienvenida
        # Crear auditoría
        # Notificar a otros servicios
```

---

### Fase 4: Microservicios (v0.5.0+)

#### 4.1 Descomposición por Bounded Contexts

```
┌─────────────────────────────────────────────────────┐
│              API Gateway (Kong/Nginx)               │
└───────────────┬─────────────────────────────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│ Auth  │  │  IoT  │  │ Users │
│Service│  │Service│  │Service│
└───────┘  └───────┘  └───────┘
```

**Servicios Propuestos:**

1. **Auth Service:**
   - Autenticación
   - Autorización
   - Gestión de tokens

2. **IoT Service:**
   - Ingesta de datos
   - Procesamiento
   - Almacenamiento

3. **User Service:**
   - Gestión de usuarios
   - Perfiles
   - Roles

4. **Notification Service:**
   - Alertas
   - Notificaciones
   - Emails

**Comunicación:**
- **Síncrona:** REST API entre servicios
- **Asíncrona:** Message Queue (RabbitMQ, Kafka)
- **Service Discovery:** Consul, Eureka

---

### Fase 5: CQRS y Event Sourcing (v0.6.0+)

#### 5.1 Command Query Responsibility Segregation

```
┌─────────────────────────────────────────┐
│         Command Side (Write)            │
│  ┌──────────┐      ┌──────────┐         │
│  │Commands │ ────▶│ Handlers │         │
│  └──────────┘      └────┬────┘         │
│                         │               │
│                         ▼               │
│                   ┌──────────┐          │
│                   │ Event    │          │
│                   │ Store    │          │
│                   └────┬─────┘          │
└────────────────────────┼────────────────┘
                         │
                         │ Events
                         │
┌────────────────────────┼────────────────┐
│         Query Side (Read)               │
│                         │               │
│                         ▼               │
│                   ┌──────────┐          │
│                   │ Read     │          │
│                   │ Models   │          │
│                   └────┬─────┘          │
│                         │               │
│                         ▼               │
│                   ┌──────────┐          │
│                   │ Queries  │          │
│                   └──────────┘         │
└─────────────────────────────────────────┘
```

**Beneficios:**
- Escalabilidad independiente de lectura/escritura
- Optimización de queries
- Historial completo de eventos
- Auditoría completa

---

## Decisiones de Diseño

### 1. Arquitectura en Capas vs Clean Architecture

**Decisión Actual:** Arquitectura en Capas  
**Razón:** Simplicidad, desarrollo rápido, equipo pequeño  
**Evolución:** Migrar gradualmente a Clean Architecture

### 2. ORM vs Repository Pattern

**Decisión Actual:** SQLAlchemy ORM directo  
**Razón:** Productividad, menos código boilerplate  
**Evolución:** Agregar Repository Pattern como abstracción

### 3. Servicios en Memoria vs Base de Datos

**Decisión Actual:** Usuarios/Roles en memoria (temporal)  
**Razón:** Desarrollo rápido, prototipo  
**Evolución:** Migrar a PostgreSQL (ya hay modelos)

### 4. Síncrono vs Asíncrono

**Decisión Actual:** Mayormente síncrono  
**Razón:** Simplicidad, FastAPI maneja bien ambos  
**Evolución:** Más operaciones async para mejor rendimiento

### 5. Monolito vs Microservicios

**Decisión Actual:** Monolito modular  
**Razón:** Menor complejidad operacional, equipo pequeño  
**Evolución:** Microservicios cuando escale (usuarios, tráfico)

---

## Principios de Diseño Aplicados

### 1. Separation of Concerns (SoC)
- ✅ Cada capa tiene responsabilidades claras
- ✅ Routers no contienen lógica de negocio
- ✅ Services no conocen detalles de HTTP

### 2. Dependency Inversion Principle (DIP)
- ⚠️ Parcial: Services dependen de implementaciones concretas
- 🔄 Mejora: Usar interfaces (ABC) para repositorios

### 3. Single Responsibility Principle (SRP)
- ✅ Cada módulo tiene una responsabilidad
- ✅ Routers solo manejan HTTP
- ✅ Services solo lógica de negocio

### 4. Don't Repeat Yourself (DRY)
- ✅ Schemas reutilizables (Pydantic)
- ✅ Dependencies compartidas
- ✅ Utilidades centralizadas

### 5. Open/Closed Principle (OCP)
- ⚠️ Mejorable: Agregar extension points
- 🔄 Mejora: Plugin system para funcionalidades

---

## Métricas de Arquitectura

### Acoplamiento
- **Actual:** Medio-Bajo
- **Objetivo:** Bajo (con Repository Pattern)

### Cohesión
- **Actual:** Alta (módulos bien definidos)
- **Objetivo:** Mantener alta cohesión

### Complejidad
- **Actual:** Baja-Media
- **Objetivo:** Mantener baja (evitar sobre-ingeniería)

### Testabilidad
- **Actual:** Media (algunos servicios en memoria)
- **Objetivo:** Alta (con interfaces y mocks)

---

## Roadmap de Evolución

### v0.2.0 - Clean Architecture Básica
- [ ] Implementar Repository Pattern
- [ ] Separar Use Cases
- [ ] Migrar servicios en memoria a DB
- [ ] Agregar interfaces (ABC)

### v0.3.0 - Arquitectura Hexagonal
- [ ] Implementar Ports and Adapters
- [ ] Desacoplar de frameworks
- [ ] Mejorar testabilidad

### v0.4.0 - Event-Driven
- [ ] Implementar Event Bus
- [ ] Domain Events
- [ ] Event Handlers

### v0.5.0 - Microservicios
- [ ] Identificar bounded contexts
- [ ] Separar en servicios
- [ ] API Gateway
- [ ] Service Discovery

### v0.6.0 - CQRS/Event Sourcing
- [ ] Separar Command/Query
- [ ] Event Store
- [ ] Read Models optimizados

---

## Comparación con Arquitecturas Conocidas

### vs MVC (Model-View-Controller)
- **Similar:** Separación de capas
- **Diferencia:** No hay "View" (API REST)
- **Equivalente:** Router (Controller) → Service → Model

### vs MVP (Model-View-Presenter)
- **Similar:** Presenter (Service) separado
- **Diferencia:** No hay View interactiva
- **Equivalente:** Router → Service (Presenter) → Model

### vs DDD (Domain-Driven Design)
- **Similar:** Modelos de dominio ricos
- **Diferencia:** No hay Aggregates explícitos aún
- **Evolución:** Implementar DDD en Fase 2

---

## Conclusión

La arquitectura actual es **sólida para el estado actual del proyecto**, con una base clara para evolucionar hacia arquitecturas más complejas según las necesidades del negocio.

**Fortalezas:**
- Separación clara de capas
- Código organizado y mantenible
- Fácil de entender y extender

**Áreas de Mejora:**
- Migrar a Repository Pattern
- Implementar Use Cases explícitos
- Mejorar testabilidad con interfaces

**Evolución Recomendada:**
1. **Corto plazo:** Clean Architecture básica
2. **Medio plazo:** Event-Driven Architecture
3. **Largo plazo:** Microservicios (si escala)

---

**Última actualización:** 2024  
**Mantenido por:** Equipo iotMonitor
