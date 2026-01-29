from flask import Flask, request, jsonify, make_response
import sqlite3
from datetime import datetime, timezone

# Initialize the Flask application
app = Flask(__name__)
DB_PATH = "spec.db"

# --- Database Helper Functions ---

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        # Use sqlite3.Row to allow accessing columns by name (e.g., row['title'])
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Initializes the database schema if it doesn't already exist."""
    conn = get_db_connection()
    if conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                completed BOOLEAN DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        conn.commit()
        conn.close()

# --- Utility Helper Functions ---

def validate_date(date_str):
    """Validates if a string is a proper ISO 8601 date format."""
    try:
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

def row_to_dict(row):
    """Converts a database row into a dictionary for JSON responses, hiding null 'updated_at'."""
    d = dict(row)
    # Hide 'updated_at' if it hasn't been set yet (matches requirement example)
    if d.get('updated_at') is None:
        d.pop('updated_at', None)
    return d

# --- API Endpoints ---

@app.route('/', methods=['GET'])
def root():
    """Root endpoint providing metadata about the API."""
    return jsonify({
        "message": "Task Management API",
        "version": "1.0.0",
        "endpoints": {
            "create_task": "POST /api/tasks",
            "list_tasks": "GET /api/tasks",
            "get_task": "GET /api/tasks/<id>",
            "update_task": "PUT /api/tasks/<id>",
            "delete_task": "DELETE /api/tasks/<id>"
        }
    }), 200

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Endpoint to create a new task."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input, JSON required"}), 400
        
        # Validation: Title is required and cannot be empty
        title = data.get('title')
        if not title or not title.strip():
            return jsonify({"error": "Title is required and cannot be empty"}), 400
        
        # Optional validation for due_date
        due_date = data.get('due_date')
        if due_date and not validate_date(due_date):
            return jsonify({"error": "Invalid date format. Use ISO format (YYYY-MM-DD)"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        # Create UTC timestamp in ISO format
        created_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        cursor = conn.cursor()
        
        # Execute INSERT query
        cursor.execute("""
            INSERT INTO tasks (title, description, due_date, completed, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (title.strip(), data.get('description'), due_date, False, created_at))
        
        task_id = cursor.lastrowid
        conn.commit()
        
        # Fetch the newly created task to return it in the response
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        new_task = cursor.fetchone()
        conn.close()

        return jsonify(row_to_dict(new_task)), 201

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Endpoint to retrieve all tasks from the database."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        # Fetch all tasks sorted by creation date (newest first)
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        rows = cursor.fetchall()
        tasks = [row_to_dict(row) for row in rows]
        conn.close()

        return jsonify({"tasks": tasks, "total": len(tasks)}), 200
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Endpoint to retrieve a specific task by its unique ID."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
             
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        conn.close()

        if task:
            return jsonify(row_to_dict(task)), 200
        
        # Return 404 if task doesn't exist
        return jsonify({"error": "Task not found"}), 404

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Endpoint to update one or more fields of an existing task."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input, JSON required"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        
        # Check if the task exists before attempting update
        cursor.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Task not found"}), 404

        # Validation: If title is provided, it cannot be empty
        title = data.get('title')
        if 'title' in data and (not title or not title.strip()):
            conn.close()
            return jsonify({"error": "Title cannot be empty"}), 400
        
        # Validation: If due_date is provided, check format
        due_date = data.get('due_date')
        if due_date and not validate_date(due_date):
            conn.close()
            return jsonify({"error": "Invalid date format. Use ISO format (YYYY-MM-DD)"}), 400

        # Dynamically build the UPDATE query based on provided fields
        update_fields = []
        update_values = []

        if 'title' in data:
            update_fields.append("title = ?")
            update_values.append(title.strip())
        if 'description' in data:
            update_fields.append("description = ?")
            update_values.append(data['description'])
        if 'due_date' in data:
            update_fields.append("due_date = ?")
            update_values.append(due_date)
        if 'completed' in data:
            update_fields.append("completed = ?")
            update_values.append(bool(data['completed']))
        
        if update_fields:
            # Add updated_at timestamp on every modification
            updated_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            update_fields.append("updated_at = ?")
            update_values.append(updated_at)
            
            update_values.append(task_id)
            query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, update_values)
            conn.commit()

        # Fetch and return the updated task object
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        updated_task = cursor.fetchone()
        conn.close()
        
        return jsonify(row_to_dict(updated_task)), 200

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Endpoint to delete an existing task by its ID."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
             
        cursor = conn.cursor()
        # Verify the task exists before deleting
        cursor.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Task not found"}), 404

        # Execute DELETE query
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Task deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

# Error Handler for generic 404 Not Found errors
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    # Ensure database is initialized before starting server
    init_db()
    # Run the Flask app on port 5000 with debug mode enabled
    app.run(debug=True, port=5000)
