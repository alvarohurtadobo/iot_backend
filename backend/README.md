# IoT Monitor

## Project Description

IoT Monitor is a IoT Platform that gathers the information of sensors installed in several machines.
IoT information is introduced with the v1/iot/ endpoints
The dashboard is served with the v1/dashboard endpoints

## Tech Stack 
### Backend
- **Python** - Main language
- **FastAPI** - Modern framework 
- **PostgreSQL** - Relational Database 
- **Docker** - Container for local and production release

### Frontend
- **Typescript** - Typed language
- **CSS Modules** - Modular Styles
- **SASS** - Prepaocesador de CSS

### Mobile
- **iOS** - Swift + SwiftUI
- **Android** - Kotlin + Jetpack Compose

## Architecture

IoT Devices (External) -------> Fast API Gateway ------> Database (PostgreSQL)
                                        |
                                        |-------> Dashboard
                                        |-------> Mobile app (Android e iOS)

## Entities
- **Business**
  - id (string)
  - name (string)
  - description (string)
  - picture_url (string)
  - created_at (string - datetime ISO)
  - updated_at (string - datetime ISO)
  - deleted_at (string - datetime ISO)

- **Branch**
  - id (string)
  - name (string)
  - description (string)
  - business_id (string) // Relacional a Business
  - representative_id (string) // Relacional a User
  - address (string)
  - created_at (string - datetime ISO)
  - updated_at (string - datetime ISO)
  - deleted_at (string - datetime ISO)

- **Machine**
  - id (string)
  - name (string)
  - description (string)
  - branch_id (string) // Relacional a Branch
  - created_at (string - datetime ISO)
  - updated_at (string - datetime ISO)
  - deleted_at (string - datetime ISO)

- **Device**
  - id (string)
  - name (string)
  - description (string)
  - machine_id (string) // Relacional a Machine
  - created_at (string - datetime ISO)
  - updated_at (string - datetime ISO)
  - deleted_at (string - datetime ISO)

- **Sensor**
  - id (string)
  - name (string)
  - description (string)
  - device_id (string) // Relacional a Device
  - type (string)
  - created_at (string - datetime ISO)
  - updated_at (string - datetime ISO)
  - deleted_at (string - datetime ISO)

- **TimeData**
  - id (string)
  - sensor_id (string) // Relacional a Sensor
  - value (float)
  - timestamp (string - datetime ISO)
  - created_at (string - datetime ISO)
  - updated_at (string - datetime ISO)
  - deleted_at (string - datetime ISO)

- **Report**
  - id (string)
  - name (string)
  - description (string)
  - business_id (string) // Relacional a Business
  - branch_id (string) // Relacional a Branch
  - machine_id (string) // Relacional a Machine
  - device_id (string) // Relacional a Device
  - time_data_ids (array of string) // Relacional a TimeData
  - created_at (string - datetime ISO)
  - updated_at (string - datetime ISO)
  - deleted_at (string - datetime ISO)

- **SensorType**
  - id (string)
  - name (string)
  - description (string)
  - created_at (string - datetime ISO)
  - updated_at (string - datetime ISO)
  - deleted_at (string - datetime ISO)

- **DeviceType**
  - id (string)
  - name (string)
  - description (string)
  - created_at (string - datetime ISO)
  - updated_at (string - datetime ISO)
  - deleted_at (string - datetime ISO)

- **User**
  - id (string)
  - first_name (string)
  - last_name (string)
  - email (string)
  - password_hash (string)
  - role_id (string) // Relacional a Role
  - created_at (string - datetime ISO)
  - updated_at (string - datetime ISO)
  - deleted_at (string - datetime ISO)

- **Role**
  - id (string)
  - name (string)
  - description (string)


