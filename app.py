from flask import Flask, request, jsonify, make_response
import sqlite3
from datetime import datetime, timezone

# Initialize Flask app
app = Flask(__name__)
DB_PATH = "spec.db"

# Database Function
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row      # sqlite3.Row to allow accessing columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():                  
    conn = get_db_connection()             
    if conn:                                   # Initial create table
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

#--------------------------------------------------------------------------------

def validate_date(date_str):                     # Validate date format
    try:
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

def row_to_dict(row):                            # Convert row to dictionary
    d = dict(row)
    if d.get('updated_at') is None:              # Hide 'updated_at' if it hasn't been set yet
        d.pop('updated_at', None)
    return d

# API Endpoints-------------------------------------------------------------------

@app.route('/', methods=['GET'])  
def root():                      #Root
    return jsonify({
        "message": "Task Management API",
        "endpoints": {
            "create_task": "POST /api/tasks",
            "list_tasks": "GET /api/tasks",
            "get_task": "GET /api/tasks/<id>",
            "update_task": "PUT /api/tasks/<id>",
            "delete_task": "DELETE /api/tasks/<id>"
        }
    }), 200

#--------------------------------------------------------------------------------

@app.route('/api/tasks', methods=['POST'])
def create_task():                              #Create Task
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input, JSON required"}), 400
        
        # Validation- Title cannot be empty
        title = data.get('title')
        if not title or not title.strip():
            return jsonify({"error": "Title cannot be empty"}), 400
        
        # validation for due_date
        due_date = data.get('due_date')
        if due_date and not validate_date(due_date):
            return jsonify({"error": "Invalid date format. Use ISO format (YYYY-MM-DD)"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        # UTC time in ISO format
        created_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        cursor = conn.execute("INSERT INTO tasks (title, description, due_date, completed, created_at) VALUES (?, ?, ?, ?, ?)",
                              (title.strip(), data.get('description'), due_date, False, created_at))
        
        task_id = cursor.lastrowid
        conn.commit()
        
        # Fetch newly created task to return it in response
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        new_task = cursor.fetchone()
        conn.close()

        return jsonify(row_to_dict(new_task)), 201

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

#--------------------------------------------------------------------------------

@app.route('/api/tasks', methods=['GET'])
def get_tasks():                    #List Tasks
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")          #Sorted by creation date
        rows = cursor.fetchall()
        tasks = [row_to_dict(row) for row in rows]
        conn.close()

        return jsonify({"tasks": tasks, "total": len(tasks)}), 200
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

#---------------------------------------------------------------------------------

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):               #Get Task
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database failed"}), 500
             
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

#---------------------------------------------------------------------------------

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):            #Update Task
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input, JSON required"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database failed"}), 500
        
        cursor = conn.cursor()
        
        # Check existance before update
        cursor.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Task missing"}), 404

        # Validation: title cannot be empty
        title = data.get('title')
        if 'title' in data and (not title or not title.strip()):
            conn.close()
            return jsonify({"error": "Title is empty"}), 400
        
        # Validation: due_date check format
        due_date = data.get('due_date')
        if due_date and not validate_date(due_date):
            conn.close()
            return jsonify({"error": "Invalid date format"}), 400

        # UPDATE query
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
            updated_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            update_fields.append("updated_at = ?")
            update_values.append(updated_at)
            
            update_values.append(task_id)
            query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, update_values)
            conn.commit()

        # Fetch and return updated task
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        updated_task = cursor.fetchone()
        conn.close()
        
        return jsonify(row_to_dict(updated_task)), 200

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

#--------------------------------------------------------------------------------

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):            #Delete Task
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database failed"}), 500
             
        cursor = conn.cursor()
        # Verify existance
        cursor.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Task missing"}), 404

        # Execute DELETE query
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Task deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

#---------------------------------------------------------------------------

@app.errorhandler(404)          # 404 Error Handler
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    init_db()                         # Initialize database before starting server
    app.run(debug=True, port=5000)
