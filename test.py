import unittest
import json
import os
from app import app, DB_PATH

class TaskApiTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_list_tasks(self):
        """Test GET /api/tasks returns 200"""
        response = self.client.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('tasks', data)
        self.assertIn('total', data)

    def test_create_task_success(self):
        """Test POST /api/tasks with valid data"""
        task_data = {
            "title": "Unit Test Task",
            "description": "Created during testing"
        }
        response = self.client.post('/api/tasks', 
                                    data=json.dumps(task_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['title'], "Unit Test Task")
        self.assertIn('id', data)

    def test_create_task_fail_no_title(self):
        """Test POST /api/tasks fails with empty title"""
        task_data = {"title": "  "}
        response = self.client.post('/api/tasks', 
                                    data=json.dumps(task_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_invalid_task(self):
        """Test GET /api/tasks/99999 returns 404"""
        response = self.client.get('/api/tasks/99999')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
