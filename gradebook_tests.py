import gradebook
import unittest
import tempfile
import os


class GradebookTestCase(unittest.TestCase):

    def setUp(self):
        self.client = gradebook.app.test_client()

    def test_root(self):
        """Tests '/' url, if its return value contains header Welcome"""
        response = self.client.get('/')
        assert b'<h1>Welcome</h1>' in response.data

if __name__ == '__main__':
    unittest.main()
