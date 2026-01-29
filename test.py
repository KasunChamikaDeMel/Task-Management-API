import unittest
from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_list(self):                     # Test list tasks
        res = self.client.get('/api/tasks')
        self.assertEqual(res.status_code, 200)

    def test_create(self):                   # Test create task
        payload = {"title": "New Task", "description": "Test doc"}
        res = self.client.post('/api/tasks', json=payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()['title'], "New Task")

    def test_create_fail(self):              # Test validation
        res = self.client.post('/api/tasks', json={"title": ""})
        self.assertEqual(res.status_code, 400)

    def test_not_found(self):                # Test 404
        res = self.client.get('/api/tasks/999')
        self.assertEqual(res.status_code, 404)

if __name__ == '__main__':
    unittest.main()
