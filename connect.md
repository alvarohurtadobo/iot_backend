# Guía de Conexión ESP32 - IoT Monitor

**Versión del Documento:** 0.0.2  
**Fecha:** 2024  
**Proyecto:** iotMonitor Backend

---

## 📋 Tabla de Contenidos

- [Introducción](#introducción)
- [Requisitos](#requisitos)
- [Configuración del Backend](#configuración-del-backend)
- [Configuración del ESP32](#configuración-del-esp32)
- [Formato de Mensajes MQTT](#formato-de-mensajes-mqtt)
- [Ejemplo de Código ESP32](#ejemplo-de-código-esp32)
- [Pruebas y Validación](#pruebas-y-validación)
- [Solución de Problemas](#solución-de-problemas)
- [Futuros Desarrollos](#futuros-desarrollos)

---

## Introducción

Este documento explica cómo conectar un dispositivo ESP32 al sistema IoT Monitor mediante el protocolo MQTT. El ESP32 puede enviar datos de sensores que serán almacenados automáticamente en la base de datos PostgreSQL del backend.

### Flujo de Datos

```
ESP32 (Sensor) → MQTT Broker → FastAPI Backend → PostgreSQL Database
```

---

## Requisitos

### Hardware
- ESP32 (cualquier variante: ESP32, ESP32-S2, ESP32-C3, etc.)
- Sensor compatible (temperatura, humedad, presión, etc.)
- Conexión WiFi

### Software
- Arduino IDE o PlatformIO
- Biblioteca PubSubClient para MQTT
- Biblioteca WiFi para ESP32

### Red
- Acceso a la red donde está el broker MQTT
- Conocer la dirección IP del broker MQTT

---

## Configuración del Backend

### Variables de Entorno

El backend debe tener configuradas las siguientes variables en el archivo `.env`:

```env
# MQTT Configuration
IOT_MONITOR_MQTT_BROKER_HOST=localhost          # IP del broker MQTT
IOT_MONITOR_MQTT_BROKER_PORT=1883               # Puerto MQTT (1883 por defecto)
IOT_MONITOR_MQTT_TOPIC=iot/data                 # Tópico MQTT (por defecto: iot/data)
IOT_MONITOR_MQTT_ENABLED=true                   # Habilitar MQTT
IOT_MONITOR_MQTT_USERNAME=                      # Usuario MQTT (opcional)
IOT_MONITOR_MQTT_PASSWORD=                      # Contraseña MQTT (opcional)
```

### Verificar Configuración

Puedes verificar que el backend está escuchando MQTT consultando el endpoint de health:

```bash
curl http://localhost:8000/v1/iot/health
```

Respuesta esperada:
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
  },
  "database": "connected"
}
```

---

## Configuración del ESP32

### 1. Instalar Bibliotecas

En Arduino IDE, instala las siguientes bibliotecas desde el Library Manager:

- **PubSubClient** (por Nick O'Leary)
- **WiFi** (incluida en el core de ESP32)
- **ArduinoJson** (opcional, para facilitar el manejo de JSON)

### 2. Configuración WiFi

Configura las credenciales de tu red WiFi:

```cpp
const char* ssid = "TU_SSID_WIFI";
const char* password = "TU_PASSWORD_WIFI";
```

### 3. Configuración MQTT

Configura la conexión al broker MQTT:

```cpp
const char* mqtt_server = "192.168.1.100";  // IP del servidor con el broker
const int mqtt_port = 1883;
const char* mqtt_topic = "iot/data";
const char* mqtt_username = "";  // Dejar vacío si no hay autenticación
const char* mqtt_password = "";  // Dejar vacío si no hay autenticación
```

---

## Formato de Mensajes MQTT

### Estructura del Mensaje JSON

El mensaje debe ser un JSON válido con la siguiente estructura:

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

### Campos Requeridos

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `sensor_id` | UUID (string) | Identificador único del sensor | `"123e4567-e89b-12d3-a456-426614174000"` |
| `device_id` | UUID (string) | Identificador único del dispositivo | `"123e4567-e89b-12d3-a456-426614174001"` |
| `value` | float | Valor numérico de la lectura | `25.5` |
| `type` | string | Tipo de dato: `"double"`, `"int"`, etc. | `"double"` |
| `timestamp` | string (ISO 8601) | Fecha y hora en formato ISO 8601 UTC | `"2024-01-01T12:00:00Z"` |

### Campos Opcionales

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `unit` | string | Unidad de medida | `"°C"`, `"kPa"`, `"%"` |

### Formato de Timestamp

El timestamp debe estar en formato ISO 8601 UTC:
- Formato: `YYYY-MM-DDTHH:MM:SSZ`
- Ejemplo: `"2024-01-15T14:30:00Z"`
- Siempre en UTC (Z al final)

### Tipos de Datos Soportados

- `"double"`: Números decimales (float)
- `"int"`: Números enteros
- Otros tipos pueden agregarse según necesidades

---

## Ejemplo de Código ESP32

### Código Completo

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>

// Configuración WiFi
const char* ssid = "TU_SSID_WIFI";
const char* password = "TU_PASSWORD_WIFI";

// Configuración MQTT
const char* mqtt_server = "192.168.1.100";  // IP del servidor
const int mqtt_port = 1883;
const char* mqtt_topic = "iot/data";
const char* mqtt_client_id = "ESP32_Client_001";
const char* mqtt_username = "";  // Opcional
const char* mqtt_password = "";  // Opcional

// UUIDs del dispositivo y sensor (generar una vez y reutilizar)
const char* device_id = "123e4567-e89b-12d3-a456-426614174001";
const char* sensor_id = "123e4567-e89b-12d3-a456-426614174000";

// Intervalo de envío (milisegundos)
const unsigned long send_interval = 30000;  // 30 segundos
unsigned long last_send = 0;

WiFiClient espClient;
PubSubClient client(espClient);

// Función para obtener timestamp ISO 8601 UTC
String getISOTimestamp() {
  time_t now = time(nullptr);
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  
  char timestamp[25];
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  return String(timestamp);
}

// Función para conectar a WiFi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// Función callback para mensajes MQTT recibidos
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensaje recibido en [");
  Serial.print(topic);
  Serial.print("]: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

// Función para reconectar a MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    
    if (client.connect(mqtt_client_id, mqtt_username, mqtt_password)) {
      Serial.println("conectado!");
    } else {
      Serial.print("falló, rc=");
      Serial.print(client.state());
      Serial.println(" intentando de nuevo en 5 segundos");
      delay(5000);
    }
  }
}

// Función para leer sensor (ejemplo: temperatura)
float readSensor() {
  // Aquí iría tu código para leer el sensor real
  // Ejemplo simulado:
  return 25.5 + (random(0, 100) / 10.0);  // Simula temperatura entre 25.5 y 35.5
}

// Función para enviar datos al broker
void sendData() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Leer sensor
  float sensor_value = readSensor();
  
  // Crear objeto JSON
  StaticJsonDocument<256> doc;
  doc["sensor_id"] = sensor_id;
  doc["device_id"] = device_id;
  doc["value"] = sensor_value;
  doc["unit"] = "°C";
  doc["type"] = "double";
  doc["timestamp"] = getISOTimestamp();

  // Serializar JSON
  char json_string[256];
  serializeJson(doc, json_string);

  // Publicar mensaje
  if (client.publish(mqtt_topic, json_string)) {
    Serial.print("Datos enviados: ");
    Serial.println(json_string);
  } else {
    Serial.println("Error al publicar mensaje");
  }
}

void setup() {
  Serial.begin(115200);
  
  // Configurar NTP para obtener hora (opcional pero recomendado)
  configTime(0, 0, "pool.ntp.org");
  
  setup_wifi();
  
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  Serial.println("ESP32 inicializado");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - last_send >= send_interval) {
    last_send = now;
    sendData();
  }
}
```

### Versión Simplificada (sin NTP)

Si no necesitas timestamps precisos, puedes usar esta versión simplificada:

```cpp
// Función para obtener timestamp ISO 8601 (sin NTP)
String getISOTimestamp() {
  // Timestamp aproximado (ajustar según necesidad)
  unsigned long seconds = millis() / 1000;
  unsigned long days = seconds / 86400;
  seconds = seconds % 86400;
  
  // Aproximación: asumiendo que el ESP32 se inició el 2024-01-01
  int year = 2024;
  int month = 1;
  int day = 1 + days;
  int hour = (seconds / 3600) % 24;
  int minute = (seconds / 60) % 60;
  int second = seconds % 60;
  
  char timestamp[25];
  snprintf(timestamp, sizeof(timestamp), "%04d-%02d-%02dT%02d:%02d:%02dZ",
           year, month, day, hour, minute, second);
  return String(timestamp);
}
```

---

## Pruebas y Validación

### 1. Verificar Conexión WiFi

```cpp
void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi conectado");
  } else {
    Serial.println("WiFi desconectado");
  }
  delay(1000);
}
```

### 2. Verificar Conexión MQTT

Usa un cliente MQTT como MQTT Explorer o mosquitto_sub para suscribirte al tópico:

```bash
mosquitto_sub -h 192.168.1.100 -t "iot/data" -v
```

### 3. Verificar Datos en la Base de Datos

Consulta los datos almacenados mediante la API:

```bash
# Verificar que el backend recibió los datos
curl http://localhost:8000/v1/iot/health
```

### 4. Monitoreo en Tiempo Real

Puedes usar herramientas como:
- **MQTT Explorer**: Cliente MQTT con interfaz gráfica
- **mosquitto_sub**: Cliente de línea de comandos
- **Node-RED**: Para visualización y procesamiento

---

## Solución de Problemas

### Problema: ESP32 no se conecta a WiFi

**Solución:**
- Verifica que el SSID y contraseña sean correctos
- Asegúrate de que la red WiFi esté en modo 2.4GHz (ESP32 no soporta 5GHz)
- Verifica la señal WiFi (RSSI)

```cpp
Serial.print("RSSI: ");
Serial.println(WiFi.RSSI());
```

### Problema: No se conecta al broker MQTT

**Solución:**
- Verifica la IP del servidor MQTT
- Verifica que el puerto 1883 esté abierto
- Revisa los logs del backend para ver errores de conexión
- Verifica que el broker MQTT esté corriendo

```cpp
Serial.print("Estado MQTT: ");
Serial.println(client.state());
// Estados: -4 (MQTT_CONNECTION_TIMEOUT), -3 (MQTT_CONNECTION_LOST), etc.
```

### Problema: Los datos no se almacenan

**Solución:**
- Verifica el formato JSON del mensaje
- Asegúrate de que los UUIDs sean válidos
- Verifica que el timestamp esté en formato ISO 8601
- Revisa los logs del backend para ver errores de validación

### Problema: Timestamp incorrecto

**Solución:**
- Configura NTP correctamente
- Usa `configTime()` antes de leer la hora
- Verifica que la zona horaria esté configurada como UTC

```cpp
configTime(0, 0, "pool.ntp.org", "time.nist.gov");
// Esperar a que se sincronice
while (time(nullptr) < 100000) {
  delay(100);
}
```

---

## Futuros Desarrollos

### Versión 0.1.0 (Próxima)

#### 1. Autenticación MQTT Mejorada
- **Autenticación por certificados TLS/SSL**
- **Autenticación por tokens JWT en mensajes MQTT**
- **Sistema de ACL (Access Control List) por dispositivo**

#### 2. QoS y Retención de Mensajes
- **Soporte para QoS 1 y QoS 2**
- **Retención de mensajes para dispositivos offline**
- **Last Will and Testament (LWT) para detectar desconexiones**

#### 3. Múltiples Tópicos
- **Tópicos específicos por dispositivo**: `iot/device/{device_id}/data`
- **Tópicos de comando**: `iot/device/{device_id}/command`
- **Tópicos de estado**: `iot/device/{device_id}/status`

#### 4. Comandos Remotos
- **Sistema de comandos desde backend hacia ESP32**
- **Actualización OTA (Over-The-Air)**
- **Configuración remota de parámetros**

### Versión 0.2.0 (Futuro)

#### 1. Protocolo MQTT sobre TLS
- **Conexión segura con certificados**
- **Puerto 8883 para MQTT sobre TLS**
- **Validación de certificados del servidor**

#### 2. Compresión de Datos
- **Compresión de payloads grandes**
- **Formato binario optimizado**
- **Batch de múltiples lecturas en un mensaje**

#### 3. Sistema de Firmware
- **Gestión de versiones de firmware**
- **Actualización OTA automática**
- **Rollback de firmware en caso de error**

#### 4. Telemetría Avanzada
- **Métricas de conexión (latencia, pérdida de paquetes)**
- **Estado de batería y energía**
- **Diagnóstico remoto del dispositivo**

### Versión 0.3.0 (Largo Plazo)

#### 1. Protocolo Alternativo: CoAP
- **Soporte para CoAP como alternativa a MQTT**
- **Mejor para dispositivos con recursos limitados**
- **Comunicación bidireccional eficiente**

#### 2. Edge Computing
- **Procesamiento de datos en el dispositivo**
- **Filtrado y agregación antes de enviar**
- **Reglas de negocio ejecutables en ESP32**

#### 3. Redes Mesh
- **Comunicación entre dispositivos ESP32**
- **Red mesh para cobertura extendida**
- **Routing automático de mensajes**

#### 4. Integración con Plataformas Cloud
- **Sincronización con AWS IoT, Azure IoT Hub**
- **Backup automático en la nube**
- **Análisis de datos con servicios cloud**

---

## Notas Adicionales

### Generación de UUIDs

Para generar UUIDs únicos para tus dispositivos y sensores, puedes usar:

**En línea:**
- https://www.uuidgenerator.net/
- https://www.uuid.org/

**En Python:**
```python
import uuid
print(uuid.uuid4())
```

**En Arduino/ESP32:**
```cpp
// Usar una librería como UUID o generar manualmente
// Ejemplo simple (no criptográficamente seguro):
String generateUUID() {
  return "123e4567-e89b-12d3-a456-" + String(random(0x1000, 0xFFFF), HEX);
}
```

### Mejores Prácticas

1. **UUIDs Estáticos**: Usa UUIDs fijos para cada dispositivo/sensor, almacenados en EEPROM o código
2. **Reconexión Automática**: Implementa lógica robusta de reconexión
3. **Watchdog**: Usa watchdog timer para reiniciar en caso de bloqueo
4. **Deep Sleep**: Para dispositivos con batería, usa deep sleep entre lecturas
5. **Validación Local**: Valida datos antes de enviar para ahorrar ancho de banda

### Recursos Adicionales

- **Documentación PubSubClient**: https://github.com/knolleary/pubsubclient
- **Documentación ESP32**: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/
- **MQTT Specification**: https://mqtt.org/mqtt-specification/
- **ISO 8601 Format**: https://en.wikipedia.org/wiki/ISO_8601

---

## Changelog

### Versión 0.0.2 (Actual)
- Agregada sección de futuros desarrollos
- Mejorada documentación de troubleshooting
- Agregados ejemplos de código simplificado
- Incluida información sobre generación de UUIDs

### Versión 0.0.1
- Versión inicial del documento
- Documentación básica de conexión ESP32
- Ejemplo de código básico

---

**Última actualización:** 2024  
**Mantenido por:** Equipo iotMonitor
