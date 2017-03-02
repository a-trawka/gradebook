from gradebook import *
import db_model
from playhouse.test_utils import test_database
import unittest


t_db = SqliteDatabase(':memory:')


class GradebookTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_homepage(self):
        resp = self.client.get('/')
        self.assertIn(b'<h1>Welcome</h1>', resp.data)

    def login_student(self, login, password):
        return self.client.post('/student_login/', data=dict(
            username=login,
            password=password
        ), follow_redirects=True)

    def login_teacher(self, login, password):
        return self.client.post('/teacher_login/', data=dict(
            username=login,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout/', follow_redirects=True)

    def test_student_login(self):
        # correct usernamme, correct password
        resp = self.login_student('atrawka', 'abc')
        self.assertIn(b"<h1>Student\'s profile</h1>", resp.data)
        resp = self.logout()
        self.assertIn(b"<h1>Welcome</h1>", resp.data)
        # correct username, incorrect password
        resp = self.login_student('atrawka', 'incorrect')
        self.assertIn(b"Wrong password", resp.data)
        # incorrect username, incorrect password
        resp = self.login_student('incorrect', 'incorrect')
        self.assertIn(b"Wrong username or password", resp.data)

    def test_teacher_login(self):
        # correct username, correct password
        resp = self.login_teacher('eunice', 'abc')
        self.assertIn(b"<h1>Teacher\'s profile</h1>", resp.data)
        resp = self.logout()
        self.assertIn(b"<h1>Welcome</h1>", resp.data)
        # correct username, incorrect password
        resp = self.login_teacher('eunice', 'incorrect')
        self.assertIn(b"Wrong password", resp.data)
        # incorrect username, incorrect password
        resp = self.login_teacher('incorrect', 'incorrect')
        self.assertIn(b"Wrong username or password", resp.data)

    def test_db(self):
        with test_database(t_db, [db_model.Subject], create_tables=True):
            # create test record
            Subject.create(name='test_subj1')
            subject = Subject.get(name='test_subj1')
            self.assertTrue(subject) # select existing record
            self.assertEqual(subject.delete_instance(), 1) # delete_instance should return 1 (number of deleted rows)
            self.assertFalse(Subject.select().where(Subject.name=='test_subj1')) # select non-existing record


if __name__ == '__main__':
    unittest.main()
