# Task Management API - System Architecture

## Overview
This application follows a **Logical Layered Architecture** implemented within a clean, single-file Flask application. It is designed for maximum simplicity, portability, and readability, strictly adhering to RESTful principles.

```mermaid
graph TD
    Client[Client (Web/Mobile/Curl)] -->|HTTP Request| API[API Layer (Flask)]
    API -->|Manual Validation| Logic[Validation & Logic]
    Logic -->|Execute SQL| DB[(SQLite Database)]
    DB -->|Return Rows| Logic
    Logic -->|Return JSON| API
    API -->|JSON Response| Client
```

## Layers

### 1. API / Presentation Layer
**Responsibility**: Routing incoming HTTP requests and returning JSON responses.
- **Technology**: Flask
- **Components**: 
  - Route Handlers (`@app.route`)
  - Error Handlers (404, 500)
  - Port: `5000`

### 2. Validation & Logic Layer
**Responsibility**: Ensure data integrity and handle business logic (like timestamping).
- **Technology**: Python Native (`if/else`, `datetime`)
- **Key Checks**:
  - `title`: Required and non-empty.
  - `due_date`: Must match ISO format.
  - Automatic `created_at` and `updated_at` generation.

### 3. Data Access Layer
**Responsibility**: Execute database commands using direct SQL.
- **Technology**: Python Standard Library (`sqlite3`)
- **Components**:
  - `get_db_connection()`: Manages safe database access.
  - `init_db()`: Self-healing database schema initialization.
  - Raw SQL queries (parameterized for security).

### 4. Persistence Layer
**Responsibility**: Store data persistently in a light-weight file.
- **Technology**: SQLite 3
- **Components**:
  - `spec.db` file.
  - `tasks` table with schema:
    - `id`: Primary Key (Auto-increment)
    - `title`, `description`, `due_date`: User data
    - `completed`: Boolean status
    - `created_at`, `updated_at`: Timestamps

## Key Design Decisions

- **Single-File Strategy**: All code is in `app.py` for easy review and submission.
- **Zero-Config Database**: SQLite requires no installation/setup, making it perfect for assessment environments.
- **Minimal Dependencies**: Switched from FastAPI/Pydantic to **Flask** to reduce the total number of external libraries, favoring standard Python logic where possible.
- **Security**: Uses parameterized queries (the `?` placeholder) to prevent SQL injection.
