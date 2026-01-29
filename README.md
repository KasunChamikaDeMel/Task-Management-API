# Task Management API
A simple REST API for managing tasks built with Flask and SQLite.

### Repository Names
- GitHub: Task-Management-API
- GitLab: Task-Management-API

## Setup

### Requirements
- Python 3.9+
- pip (or npm)

### Installation
1. Clone the repository
2. Install dependencies: pip install -r requirements.txt
3. Run the application: python app.py
4. API runs at: http://localhost:5000



## Testing the API - curl ------------------------------------

### Create a task
curl -X POST http://localhost:5000/api/tasks 
-H "Content-Type: application/json" 
-d '{"title": "Test task", "description": "Testing the API"}'

### List all tasks
curl http://localhost:5000/api/tasks

### Get a single task
curl http://localhost:5000/api/tasks/1

### Update a task
curl -X PUT http://localhost:5000/api/tasks/1 
-H "Content-Type: application/json" 
-d '{"completed": true}'

### Delete a task
curl -X DELETE http://localhost:5000/api/tasks/1


## Testing with Postman ------------------------------------

You can find the Postman collection file postman.json in the root directory.

To use it:
1. Open Postman.
2. Click on the Import button.
3. Drag and drop the postman.json file or select it from your file system.
4. Once imported, you will see a collection named Task Management API with all the requests pre-configured.


## Notes
- Used SQLite (spec.db) for simplicity and "zero-config" persistence.
- Clean Code: Follows REST conventions with standard HTTP status codes (200, 201, 404, etc.).
- Validation: Includes basic checks for required titles and date formats.
