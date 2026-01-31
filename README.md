# IoT Backend

Backend para centralización de datos de múltiples dispositivos IoT. Plataforma FastAPI que recibe datos de sensores mediante MQTT y HTTP, almacenándolos en PostgreSQL y proporcionando una API REST para dashboards y aplicaciones móviles.

## 📋 Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Stack Tecnológico](#stack-tecnológico)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución con Docker](#ejecución-con-docker)
- [Migraciones de Base de Datos](#migraciones-de-base-de-datos)
- [MQTT](#mqtt)
- [API REST](#api-rest)
- [Integración con Frontend React](#integración-con-frontend-react)
- [Endpoints Disponibles](#endpoints-disponibles)

## 🏗️ Arquitectura

```
┌─────────────────┐
│  IoT Devices    │
│  (Sensores)     │
└────────┬────────┘
         │
         │ MQTT / HTTP
         │
┌────────▼─────────────────────────────────────┐
│         FastAPI Gateway                       │
│  ┌─────────────────────────────────────────┐ │
│  │  MQTT Client (paho-mqtt)               │ │
│  │  - Escucha tópico: iot/data            │ │
│  │  - Valida y almacena TimeData          │ │
│  └─────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────┐ │
│  │  REST API (FastAPI)                     │ │
│  │  - /v1/auth/* (Autenticación JWT)       │ │
│  │  - /v1/users/* (Gestión de usuarios)    │ │
│  │  - /v1/roles/* (Gestión de roles)       │ │
│  │  - /v1/iot/* (Datos IoT)                │ │
│  └─────────────────────────────────────────┘ │
└────────┬───────────────────────────────────────┘
         │
         │ SQLAlchemy ORM
         │
┌────────▼────────┐
│   PostgreSQL     │
│   (Base de datos)│
└──────────────────┘
         │
         │
┌────────▼────────┐
│   Dashboard     │
│   (React)       │
└─────────────────┘
```

### Flujo de Datos

1. **Ingesta de Datos IoT**:
   - Los dispositivos IoT envían datos mediante MQTT al tópico `iot/data`
   - El cliente MQTT valida los mensajes con Pydantic
   - Los datos se almacenan automáticamente en PostgreSQL

2. **API REST**:
   - El dashboard y aplicaciones móviles consumen datos mediante endpoints REST
   - Los datos se consultan desde PostgreSQL usando SQLAlchemy ORM
   - Autenticación JWT protege los endpoints sensibles

3. **Seguridad**:
   - Autenticación JWT (access y refresh tokens)
   - Rate limiting y bloqueo de cuenta
   - Auditoría de intentos de login
   - Validación de contraseñas fuertes

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.11+** - Lenguaje principal
- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy 2.0** - ORM para acceso a datos
- **Alembic** - Migraciones de base de datos
- **Pydantic** - Validación de datos y configuración
- **paho-mqtt** - Cliente MQTT para recepción de datos IoT
- **python-jose** - JWT para autenticación
- **passlib** - Hash de contraseñas (bcrypt)
- **uv** - Gestor de dependencias y entornos virtuales
- **Uvicorn** - Servidor ASGI de alto rendimiento

### Frontend (Planeado)
- **TypeScript** - Lenguaje tipado
- **React** - Framework de UI
- **CSS Modules** - Estilos modulares
- **SASS** - Preprocesador CSS

### Mobile (Planeado)
- **iOS**: Swift + SwiftUI
- **Android**: Kotlin + Jetpack Compose

## 📁 Estructura del Proyecto

```
iot_backend/
├── backend/
│   ├── iot_monitor/              # Aplicación principal
│   │   ├── alembic/              # Migraciones de base de datos
│   │   │   ├── versions/         # Archivos de migración
│   │   │   └── env.py           # Configuración Alembic
│   │   ├── app/
│   │   │   ├── api/             # Endpoints REST
│   │   │   │   ├── routers/    # Routers de FastAPI
│   │   │   │   │   ├── auth.py    # Autenticación
│   │   │   │   │   ├── users.py   # Usuarios
│   │   │   │   │   └── roles.py   # Roles
│   │   │   │   ├── schemas/    # Schemas Pydantic para API
│   │   │   │   └── dependencies/  # Dependencias (auth, etc.)
│   │   │   ├── core/           # Configuración central
│   │   │   │   ├── config.py  # Settings y variables de entorno
│   │   │   │   ├── security.py   # JWT, hashing
│   │   │   │   └── rate_limit.py # Rate limiting
│   │   │   ├── db/             # Base de datos
│   │   │   ├── models/         # Modelos SQLAlchemy
│   │   │   └── base.py         # Configuración SQLAlchemy
│   │   │   ├── services/       # Servicios de negocio
│   │   │   │   ├── users.py   # Servicio de usuarios
│   │   │   │   └── roles.py   # Servicio de roles
│   │   │   ├── iot_data/       # Módulo de datos IoT
│   │   │   │   ├── router.py     # Endpoints IoT
│   │   │   │   ├── schemas.py    # Schemas IoT
│   │   │   │   └── time_data_service.py  # Servicio TimeData
│   │   │   ├── mqtt/           # Cliente MQTT
│   │   │   │   ├── client.py  # Cliente paho-mqtt
│   │   │   │   └── schemas.py # Schemas para mensajes MQTT
│   │   │   └── main.py         # Punto de entrada FastAPI
│   │   ├── docker-compose.yml  # Configuración Docker Compose
│   │   ├── Dockerfile          # Imagen Docker
│   │   ├── pyproject.toml      # Dependencias y configuración
│   │   └── alembic.ini         # Configuración Alembic
│   └── specs/                   # Especificaciones del proyecto
│       ├── 00_contracts.md     # Contratos de entidades y endpoints
│       └── 01_setup.md         # Guía de configuración
└── frontend/                    # Frontend React (pendiente)
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.11 o superior
- PostgreSQL 15 o superior
- Docker y Docker Compose (opcional, para desarrollo con contenedores)
- uv (gestor de dependencias Python) - [Instalación](https://github.com/astral-sh/uv)

### Instalación Local

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd iot_backend
```

2. **Navegar al directorio del backend**:
```bash
cd backend/iot_monitor
```

3. **Crear entorno virtual e instalar dependencias**:
```bash
# Crear entorno virtual
uv venv --python 3.11

# Activar entorno virtual
# En Linux/Mac:
source .venv/bin/activate
# En Windows:
# .venv\Scripts\activate

# Instalar dependencias
uv sync
```

4. **Configurar variables de entorno**:
```bash
# Crear archivo .env en backend/iot_monitor/
cp .env.example .env  # Si existe, o crear manualmente
```

Editar `.env` con tus configuraciones:
```env
IOT_MONITOR_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/iot_monitor
IOT_MONITOR_MQTT_BROKER_HOST=localhost
IOT_MONITOR_MQTT_BROKER_PORT=1883
IOT_MONITOR_MQTT_TOPIC=iot/data
IOT_MONITOR_MQTT_ENABLED=true
IOT_MONITOR_SECRET_KEY=tu-secret-key-seguro-aqui-cambiar-en-produccion
```

**Nota:** Cambiar `IOT_MONITOR_SECRET_KEY` en producción. Ver `app/core/config.py` para todas las variables disponibles.

5. **Iniciar PostgreSQL** (si no usas Docker):
```bash
# Asegúrate de que PostgreSQL esté corriendo
# Crear base de datos
createdb iot_monitor
```

6. **Ejecutar migraciones**:
```bash
# Aplicar migraciones de base de datos
uv run alembic upgrade head
```

7. **Iniciar el servidor**:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en `http://localhost:8000`

- **Documentación interactiva**: `http://localhost:8000/docs`
- **Documentación alternativa**: `http://localhost:8000/redoc`

## 🐳 Ejecución con Docker

### Usando Docker Compose (Recomendado)

1. **Navegar al directorio del backend**:
```bash
cd backend/iot_monitor
```

2. **Iniciar servicios** (PostgreSQL + API):
```bash
docker-compose up -d
```

3. **Aplicar migraciones**:
```bash
# Ejecutar migraciones dentro del contenedor
docker-compose exec api uv run alembic upgrade head
```

4. **Ver logs**:
```bash
docker-compose logs -f api
```

5. **Detener servicios**:
```bash
docker-compose down
```

### Variables de Entorno en Docker

Las variables de entorno se pueden configurar en `docker-compose.yml` o mediante un archivo `.env`:

```yaml
environment:
  IOT_MONITOR_DATABASE_URL: postgresql+psycopg2://postgres:postgres@db:5432/iot_monitor
  IOT_MONITOR_MQTT_BROKER_HOST: mosquitto  # Si tienes un broker MQTT en Docker
  IOT_MONITOR_MQTT_BROKER_PORT: 1883
  IOT_MONITOR_MQTT_ENABLED: "true"
```

### Agregar Broker MQTT a Docker Compose

Para agregar un broker MQTT (Mosquitto) a tu stack, agrega esto a `docker-compose.yml`:

```yaml
services:
  mqtt:
    image: eclipse-mosquitto:latest
    container_name: iot_monitor_mqtt
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
    networks:
      - default
```

Y actualiza la configuración de la API:
```yaml
environment:
  IOT_MONITOR_MQTT_BROKER_HOST: mqtt
```

## 🗄️ Migraciones de Base de Datos

El proyecto usa Alembic para gestionar migraciones de base de datos.

### Comandos Útiles

```bash
# Crear una nueva migración (después de modificar modelos)
uv run alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones pendientes
uv run alembic upgrade head

# Revertir última migración
uv run alembic downgrade -1

# Ver historial de migraciones
uv run alembic history

# Ver estado actual
uv run alembic current
```

### Modelos de Base de Datos

El proyecto incluye los siguientes modelos (entidades):

- **Role** - Roles de usuario
- **User** - Usuarios del sistema
- **Business** - Empresas/clientes
- **Branch** - Sucursales
- **Machine** - Máquinas
- **DeviceType** - Tipos de dispositivos
- **Device** - Dispositivos IoT
- **SensorType** - Tipos de sensores
- **Sensor** - Sensores
- **TimeData** - Datos temporales de sensores
- **Report** - Reportes generados
- **LoginAudit** - Auditoría de intentos de login
- **RevokedToken** - Tokens JWT revocados

Ver `db.md` para documentación completa de la base de datos y `backend/specs/00_contracts.md` para detalles de cada entidad.

## 📡 MQTT

El sistema incluye un cliente MQTT que escucha mensajes de dispositivos IoT y los almacena automáticamente en la base de datos.

### Configuración MQTT

Variables de entorno disponibles:

```env
IOT_MONITOR_MQTT_BROKER_HOST=localhost        # Host del broker MQTT
IOT_MONITOR_MQTT_BROKER_PORT=1883            # Puerto del broker
IOT_MONITOR_MQTT_USERNAME=usuario            # Usuario (opcional)
IOT_MONITOR_MQTT_PASSWORD=contraseña         # Contraseña (opcional)
IOT_MONITOR_MQTT_TOPIC=iot/data              # Tópico al que suscribirse
IOT_MONITOR_MQTT_CLIENT_ID=iot_monitor_client # ID del cliente
IOT_MONITOR_MQTT_ENABLED=true                # Habilitar/deshabilitar MQTT
```

### Formato de Mensaje MQTT

Los dispositivos IoT deben enviar mensajes JSON al tópico configurado (`iot/data` por defecto) con el siguiente formato:

```json
{
  "sensor_id": "123e4567-e89b-12d3-a456-426614174000",
  "device_id": "123e4567-e89b-12d3-a456-426614174001",
  "value": 25.5,
  "unit": "°C",
  "type": "double",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Ejemplo de Publicación MQTT

```bash
# Usando mosquitto_pub
mosquitto_pub -h localhost -p 1883 -t iot/data -m '{
  "sensor_id": "123e4567-e89b-12d3-a456-426614174000",
  "device_id": "123e4567-e89b-12d3-a456-426614174001",
  "value": 25.5,
  "unit": "°C",
  "type": "double",
  "timestamp": "2024-01-01T12:00:00Z"
}'
```

### Conectar Dispositivos ESP32

Guía pendiente de documentar (no hay archivo `connect.md` en este repositorio).

### Estado del Cliente MQTT

Puedes verificar el estado del cliente MQTT mediante el endpoint `/health`:

```bash
curl http://localhost:8000/health
```

Respuesta:
```json
{
  "status": "ok",
  "service": "iotMonitor",
  "version": "0.1.0",
  "mqtt": {
    "enabled": true,
    "status": "connected",
    "broker": "localhost:1883",
    "topic": "iot/data"
  }
}
```

## 🔌 API REST

### Base URL

```
http://localhost:8000/v1
```

### Autenticación

La API utiliza **autenticación JWT** (JSON Web Tokens) para proteger los endpoints.

**Flujo de Autenticación:**

1. **Login**: `POST /v1/auth/login` - Obtener tokens de acceso y actualización
2. **Usar Token**: Incluir `Authorization: Bearer <access_token>` en headers
3. **Refresh Token**: `POST /v1/auth/refresh` - Renovar access_token cuando expire
4. **Logout**: `POST /v1/auth/logout` - Revocar refresh_token

**Características de Seguridad:**
- Tokens JWT con expiración (access: 30 min, refresh: 7 días)
- Rate limiting en login (5 intentos por minuto)
- Bloqueo de cuenta después de múltiples intentos fallidos (5 intentos = 30 min bloqueado)
- Auditoría de intentos de login
- Revocación de tokens al cerrar sesión
- Validación de contraseñas fuertes

### Formato de Respuesta

Todas las respuestas JSON siguen el formato estándar de FastAPI.

Ver `docs.md` y `endpoint.md` para documentación completa de endpoints.

## 📋 Endpoints Disponibles

### Endpoints Raíz

- `GET /` - Mensaje de bienvenida
- `GET /health` - Estado del servicio y cliente MQTT

### Autenticación (`/v1/auth`)

**Nota:** Estos endpoints no requieren autenticación.

- `POST /v1/auth/login` - Iniciar sesión y obtener tokens JWT
- `POST /v1/auth/refresh` - Renovar access token
- `POST /v1/auth/logout` - Cerrar sesión (revocar token)

### Roles (`/v1/roles`)

- `GET /v1/roles/` - Listar todos los roles
- `POST /v1/roles/` - Crear nuevo rol
- `GET /v1/roles/{role_id}` - Obtener rol por ID
- `PUT /v1/roles/{role_id}` - Actualizar rol
- `DELETE /v1/roles/{role_id}` - Eliminar rol

### Usuarios (`/v1/users`)

**Autenticación requerida** (excepto donde se indique)

- `GET /v1/users/` - Listar usuarios activos
- `POST /v1/users/` - Crear nuevo usuario
- `GET /v1/users/{user_id}` - Obtener usuario por ID
- `PUT /v1/users/{user_id}` - Actualizar usuario
- `DELETE /v1/users/{user_id}` - Eliminar usuario (soft delete)
- `GET /v1/users/me` - Obtener información del usuario actual (autenticado)

### IoT (`/v1/iot`)

- `POST /v1/iot/data` - Enviar datos IoT individuales (alternativa a MQTT)
- `POST /v1/iot/many` - Enviar múltiples datos IoT en lote
- `POST /v1/iot/register` - Registrar estado de dispositivo IoT
- `POST /v1/iot/update` - Actualizar estado de dispositivo IoT
- `GET /v1/iot/health` - Health check del servicio IoT (estado de MQTT y DB)

Ver `docs.md` para documentación detallada de todos los endpoints y `endpoint.md` para casos de uso del panel de administración.

## ⚛️ Integración con Frontend React

### Configuración Base

1. **Crear archivo de configuración** en tu proyecto React (`src/config/api.ts`):

```typescript
export const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  apiVersion: 'v1',
  timeout: 10000,
};

export const API_ENDPOINTS = {
  health: '/health',
  auth: {
    login: '/v1/auth/login',
    refresh: '/v1/auth/refresh',
    logout: '/v1/auth/logout',
  },
  roles: '/v1/roles',
  users: '/v1/users',
  usersMe: '/v1/users/me',
  iot: {
    data: '/v1/iot/data',
    many: '/v1/iot/many',
    register: '/v1/iot/register',
    update: '/v1/iot/update',
    health: '/v1/iot/health',
  },
};
```

2. **Crear servicio de API** (`src/services/api.ts`):

```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { API_CONFIG, API_ENDPOINTS } from '../config/api';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.baseURL,
      timeout: API_CONFIG.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token de autenticación
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Interceptor para manejar errores y refresh token
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            // Intentar refrescar token
            const refreshToken = localStorage.getItem('refresh_token');
            const response = await axios.post(
              `${API_CONFIG.baseURL}${API_ENDPOINTS.auth.refresh}`,
              { refresh_token: refreshToken }
            );
            
            const { access_token, refresh_token: newRefreshToken } = response.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', newRefreshToken);
            
            // Reintentar request original
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            // Si falla refresh, redirigir a login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async getHealth() {
    const response = await this.client.get(API_ENDPOINTS.health);
    return response.data;
  }

  // Roles
  async getRoles() {
    const response = await this.client.get(API_ENDPOINTS.roles);
    return response.data;
  }

  async createRole(data: any) {
    const response = await this.client.post(API_ENDPOINTS.roles, data);
    return response.data;
  }

  // Usuarios
  async getUsers() {
    const response = await this.client.get(API_ENDPOINTS.users);
    return response.data;
  }

  async createUser(data: any) {
    const response = await this.client.post(API_ENDPOINTS.users, data);
    return response.data;
  }

  // Autenticación
  async login(email: string, password: string) {
    const response = await this.client.post(API_ENDPOINTS.auth.login, {
      email,
      password,
    });
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    return response.data;
  }

  async logout() {
    const refreshToken = localStorage.getItem('refresh_token');
    await this.client.post(API_ENDPOINTS.auth.logout, {
      refresh_token: refreshToken,
    });
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // Usuario actual
  async getCurrentUser() {
    const response = await this.client.get(API_ENDPOINTS.usersMe);
    return response.data;
  }

  // IoT Data
  async sendIoTData(data: any) {
    const response = await this.client.post(API_ENDPOINTS.iot.data, data);
    return response.data;
  }

  async sendBulkIoTData(data: any[]) {
    const response = await this.client.post(API_ENDPOINTS.iot.many, data);
    return response.data;
  }
}

export const apiService = new ApiService();
```

3. **Usar en componentes React**:

```typescript
import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';

const UsersList: React.FC = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await apiService.getUsers();
        setUsers(data);
      } catch (error) {
        console.error('Error fetching users:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {users.map((user: any) => (
          <li key={user.id}>{user.email}</li>
        ))}
      </ul>
    </div>
  );
};

export default UsersList;
```

### Variables de Entorno en React

Crear archivo `.env` en la raíz del proyecto React:

```env
REACT_APP_API_URL=http://localhost:8000
```

### CORS

Si tu frontend React corre en un puerto diferente (ej: `http://localhost:3000`), necesitarás configurar CORS en FastAPI.

Agregar en `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL de tu frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Ejemplo Completo con React Query

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';

// Hook para obtener usuarios
export const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => apiService.getUsers(),
  });
};

// Hook para crear usuario
export const useCreateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: any) => apiService.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
};
```

## 🧪 Testing

```bash
# Ejecutar tests
uv run pytest

# Con cobertura
uv run pytest --cov=app tests/

# Ejecutar tests específicos
uv run pytest tests/test_iot_router.py
```

## 🔍 Características Implementadas

### Seguridad
- ✅ Autenticación JWT (access y refresh tokens)
- ✅ Hash de contraseñas con bcrypt
- ✅ Validación de contraseñas fuertes
- ✅ Rate limiting en login
- ✅ Bloqueo de cuenta por intentos fallidos
- ✅ Auditoría de intentos de login
- ✅ Revocación de tokens

### Logging
- ✅ Logging estructurado en todos los endpoints
- ✅ Logging de operaciones exitosas
- ✅ Logging de errores con contexto
- ✅ Traceback completo para debugging

### Base de Datos
- ✅ Migraciones con Alembic
- ✅ Soft delete en entidades principales
- ✅ Timestamps automáticos (created_at, updated_at)
- ✅ Relaciones entre entidades bien definidas

### IoT
- ✅ Recepción de datos por MQTT
- ✅ Recepción de datos por HTTP REST
- ✅ Validación de datos con Pydantic
- ✅ Almacenamiento automático en PostgreSQL
- ✅ Health check del servicio IoT

## 📚 Documentación Adicional

### Documentación del Proyecto

- **`docs.md`** - Documentación resumida de todos los endpoints
- **`endpoint.md`** - Guía de endpoints para panel de administración (casos de uso)
- **`db.md`** - Documentación completa de la base de datos (tablas, relaciones, campos)
- **`MEJORAS.md`** - Sugerencias de mejoras pequeñas para el código
- **`backend/specs/00_contracts.md`** - Contratos de entidades y endpoints
- **`backend/specs/01_setup.md`** - Guía de configuración

### Documentación Técnica

- **Documentación FastAPI**: `http://localhost:8000/docs` (cuando el servidor está corriendo)
- **Documentación ReDoc**: `http://localhost:8000/redoc` (documentación alternativa)

### Comandos Útiles (Makefile)

Si tienes `make` instalado, puedes usar:

```bash
cd backend/iot_monitor

make start       # Iniciar servicios (Docker)
make stop        # Detener servicios
make restart     # Reiniciar servicios
make logs        # Ver logs en tiempo real
make build       # Construir imágenes Docker
make clean       # Limpiar contenedores y volúmenes
make help        # Mostrar ayuda
```

Ver `backend/iot_monitor/Makefile` para todos los comandos disponibles.

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

[Especificar licencia]

## 👥 Autores

- Equipo iotMonitor

---

## 🚀 Ejecución Rápida

### Opción 1: Con Docker (Recomendado)

```bash
cd backend/iot_monitor
make start
```

### Opción 2: Local

```bash
cd backend/iot_monitor
uv venv --python 3.11
source .venv/bin/activate
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

---

**Nota**: Este proyecto está en desarrollo activo. Consulta la documentación en `docs.md`, `endpoint.md` y `architecture.md` para más detalles.

