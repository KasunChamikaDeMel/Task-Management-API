# Assessment-ToDo (Flask)

A simple REST API for managing tasks (to-do list) built with **Flask** and **SQLite**.

## Setup

### Requirements
- Python 3.9+
- pip (or npm)

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. API runs at: `http://localhost:5000`

## Testing the API

### Create a task
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Testing the API"}'
```

### List all tasks
```bash
curl http://localhost:5000/api/tasks
```

### Get a single task
```bash
curl http://localhost:5000/api/tasks/1
```

### Update a task
```bash
curl -X PUT http://localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Delete a task
```bash
curl -X DELETE http://localhost:5000/api/tasks/1
```

## Notes
- Used **SQLite** (`spec.db`) for simplicity and "zero-config" persistence.
- **Clean Code**: Follows REST conventions with standard HTTP status codes (200, 201, 404, etc.).
- **Validation**: Includes basic checks for required titles and date formats.
