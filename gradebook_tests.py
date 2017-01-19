import gradebook
import unittest


class GradebookTestCase(unittest.TestCase):

    def setUp(self):
        self.client = gradebook.app.test_client()

    def test_root(self):
        """Checks if '/' response data contains a header Welcome"""
        response = self.client.get('/')
        self.assertIn(b'<h1>Welcome</h1>', response.data)

if __name__ == '__main__':
    unittest.main()
