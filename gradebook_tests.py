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

    #misc
    def login_student(self, login, password):
        return self.client.post('/student_login/', data=dict(
            username=login,
            password=password
        ), follow_redirects=True)

    #misc
    def login_teacher(self, login, password):
        return self.client.post('/teacher_login/', data=dict(
            username=login,
            password=password
        ), follow_redirects=True)

    #misc
    def logout(self):
        return self.client.get('/logout/', follow_redirects=True)

    def test_student_login(self):
        resp = self.login_student('atrawka', 'abc')  # correct username, correct password
        self.assertIn(b"<h1>Student\'s profile</h1>", resp.data)
        resp = self.logout()
        self.assertIn(b"<h1>Welcome</h1>", resp.data)
        resp = self.login_student('atrawka', 'incorrect')  # correct username, incorrect password
        self.assertIn(b"Wrong password", resp.data)
        resp = self.login_student('incorrect', 'incorrect')  # incorrect username, incorrect password
        self.assertIn(b"Wrong username or password", resp.data)

    def test_teacher_login(self):
        resp = self.login_teacher('eunice', 'abc')  # correct username, correct password
        self.assertIn(b"<h1>Teacher\'s profile</h1>", resp.data)
        resp = self.logout()
        self.assertIn(b"<h1>Welcome</h1>", resp.data)
        resp = self.login_teacher('eunice', 'incorrect')  # correct username, incorrect password
        self.assertIn(b"Wrong password", resp.data)
        resp = self.login_teacher('incorrect', 'incorrect')  # incorrect username, incorrect password
        self.assertIn(b"Wrong username or password", resp.data)

    def test_db_specialization(self):
        with test_database(
                t_db,
                [db_model.Subject,
                 db_model.Teacher,
                 db_model.TeacherSubject],
                create_tables=True):
            test_subject = Subject.create(name='test_subject')
            test_teacher = Teacher.create(first_name='test', last_name='test', username='test_teacher', password='test')
            test_specialization = TeacherSubject.create(teacher=test_teacher, specialization=test_subject)
            self.assertTrue(test_subject)
            self.assertTrue(test_teacher)
            self.assertTrue(test_specialization)
            self.assertTrue(test_teacher.delete_instance(recursive=True))  # delete teacher and its dependencies
            self.assertTrue(test_subject.delete_instance())
            self.assertFalse(TeacherSubject.select().where(TeacherSubject.teacher == test_teacher,
                                                           TeacherSubject.specialization == test_subject))
            self.assertFalse(Teacher.select().where(Teacher.username == 'test_teacher'))
            self.assertFalse(Subject.select().where(Subject.name == 'test_subject'))

    def test_db_grading(self):
        with test_database(
                t_db,
                [db_model.Student,
                 db_model.Teacher,
                 db_model.Subject,
                 db_model.Grade],
                create_tables=True):
            test_subject_1 = Subject.create(name='test_subject1')
            test_subject_2 = Subject.create(name='test_subject2')
            test_teacher = Teacher.create(first_name='test', last_name='test', username='test_teacher', password='test')
            test_student = Student.create(first_name='test', last_name='test', group='test', username='test_student',
                                          password='test')
            self.assertTrue(test_subject_1)
            self.assertTrue(test_subject_2)
            self.assertTrue(test_teacher)
            self.assertTrue(test_student)
            test_grade_1 = Grade.create(student=test_student, subject=test_subject_1, teacher=test_teacher, grade='1')
            test_grade_2 = Grade.create(student=test_student, subject=test_subject_2, teacher=test_teacher, grade='2')
            self.assertTrue(test_grade_1)
            self.assertTrue(test_grade_2)
            self.assertTrue(test_subject_1.delete_instance(recursive=True))  # delete subject and its dependencies
            self.assertFalse(Grade.select().where(Grade.grade == '1'))
            self.assertTrue(test_grade_2.delete_instance())
            self.assertTrue(test_subject_2.delete_instance())
            self.assertTrue(test_teacher.delete_instance())
            self.assertTrue(test_student.delete_instance())


if __name__ == '__main__':
    unittest.main()
