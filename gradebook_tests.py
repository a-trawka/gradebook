from playhouse.test_utils import test_database
from bcrypt import hashpw, gensalt
from gradebook import app
import model
import unittest


class DefaultGetNoUserTest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_homepage(self):
        resp = self.client.get('/')
        self.assertIn(b"<h1>Welcome</h1>", resp.data)

    def test_get_student_login(self):
        resp = self.client.get('/student_login/')
        self.assertIn(b"<h2>Log in as a student</h2>", resp.data)

    def test_get_student_profile(self):
        """/student_profile/ should return homepage, since it requires to be logged in as a student."""
        resp = self.client.get('/student_profile/', follow_redirects=True)
        self.assertIn(b"<h1>Welcome</h1>", resp.data)

    def test_get_student_profile_foreign(self):
        """/student_profile/<username> should return homepage, since it requires to be logged in as a teacher."""
        resp = self.client.get('/student_profile/test', follow_redirects=True)
        self.assertIn(b"<h1>Welcome</h1>", resp.data)

    def test_get_add_grade(self):
        """/add_grade/ should return homepage, since it requires to be logged in as a teacher."""
        resp = self.client.get('/add_grade/', follow_redirects=True)
        self.assertIn(b"<h1>Welcome</h1>", resp.data)

    def test_get_teacher_login(self):
        resp = self.client.get('/teacher_login/')
        self.assertIn(b"<h2>Log in as a teacher</h2>", resp.data)

    def test_get_teacher_profile(self):
        """/student_profile/ should return homepage, since it requires to be logged in as a teacher."""
        resp = self.client.get('/teacher_profile/', follow_redirects=True)
        self.assertIn(b"<h1>Welcome</h1>", resp.data)

    def test_get_groups(self):
        resp = self.client.get('/groups/', follow_redirects=True)
        self.assertIn(b"<h1>Welcome</h1>", resp.data)

    def test_get_group(self):
        resp = self.client.get('/group/', follow_redirects=True)
        self.assertIn(b"<h1>Welcome</h1>", resp.data)

    def test_get_group_foreign(self):
        resp = self.client.get('/group/0', follow_redirects=True)
        self.assertIn(b"<h1>Welcome</h1>", resp.data)

    def test_get_logout(self):
        """ /logout/ redirects to /student_login if user is not logged in."""
        resp = self.client.get('/logout/', follow_redirects=True)
        self.assertIn(b"<h2>Log in as a student</h2>", resp.data)


class AdminPanelTest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_get_admin_login(self):
        resp = self.client.get('/admin/login/')
        self.assertIn(b"ID", resp.data)
        self.assertIn(b"PSWD", resp.data)


class DatabaseOperationsTest(unittest.TestCase):
    model.get_db().init('test_db.db')
    _student_template = {'first_name': 'test',
                         'last_name': 'test',
                         'group': 'test',
                         'username': 'test_student',
                         'password': 'test'}
    _teacher_template = {'first_name': 'test',
                         'last_name': 'test',
                         'username': 'test_teacher',
                         'password': 'test'}
    _table_model = [model.Student, model.Teacher, model.Subject, model.Grade, model.TeacherSubject]

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        model.get_db().drop_tables(self._table_model, safe=True)

    def test_db_student(self):
        with test_database(model.get_db(), [model.Student], create_tables=True, drop_tables=True):
            test_student = model.Student.create(**self._student_template)
            self.assertTrue(test_student)
            self.assertEqual(test_student, model.Student.get(model.Student.username == 'test_student'))
            self.assertTrue(test_student.delete_instance())

    def test_db_teacher(self):
        with test_database(model.get_db(), [model.Teacher], create_tables=True, drop_tables=True):
            test_teacher = model.Teacher.create(**self._teacher_template)
            self.assertTrue(test_teacher)
            self.assertEqual(test_teacher, model.Teacher.get(model.Teacher.username == 'test_teacher'))
            self.assertTrue(test_teacher.delete_instance())

    def test_db_subject(self):
        with test_database(model.get_db(), [model.Subject], create_tables=True, drop_tables=True):
            test_subject = model.Subject.create(name='test_subject')
            self.assertTrue(test_subject)
            self.assertEqual(test_subject, model.Subject.get(model.Subject.name == 'test_subject'))
            self.assertTrue(test_subject.delete_instance())

    def test_db_specialization(self):
        """Create few test records needed to create TeacherSubject object.
        This covers tests of: 
        - creating TeacherSubject object
        - deleting teacher/subject recursively, what leads to deleting dependent TeacherSubject object
        """
        with test_database(model.get_db(), self._table_model, create_tables=True, drop_tables=True):
            test_subject = model.Subject.create(name='test_subject')
            test_teacher = model.Teacher.create(**self._teacher_template)
            test_specialization = model.TeacherSubject.create(teacher=test_teacher, specialization=test_subject)
            self.assertTrue(test_specialization)
            self.assertTrue(test_teacher.delete_instance(recursive=True))  # delete teacher and its dependencies
            self.assertTrue(test_subject.delete_instance())
            self.assertFalse(model.TeacherSubject.select().where(
                model.TeacherSubject.teacher == test_teacher,
                model.TeacherSubject.specialization == test_subject))
            self.assertFalse(model.Teacher.select().where(model.Teacher.username == 'test_teacher'))
            self.assertFalse(model.Subject.select().where(model.Subject.name == 'test_subject'))

    def test_db_grading(self):
        """Create few test records needed to test grading system.
        This covers tests of:
        - creating Grade object
        - deleting objects which Grade object is dependent on, what results in deleting the grade as well
        """
        with test_database(model.get_db(), self._table_model, create_tables=True, drop_tables=True):
            test_subject_1 = model.Subject.create(name='test_subject1')
            test_subject_2 = model.Subject.create(name='test_subject2')
            test_teacher = model.Teacher.create(**self._teacher_template)
            test_student = model.Student.create(**self._student_template)
            test_grade_1 = model.Grade.create(student=test_student, subject=test_subject_1, teacher=test_teacher,
                                              grade='1')
            test_grade_2 = model.Grade.create(student=test_student, subject=test_subject_2, teacher=test_teacher,
                                              grade='2')
            self.assertTrue(test_grade_1)
            self.assertTrue(test_grade_2)
            self.assertTrue(test_subject_1.delete_instance(recursive=True))  # delete subject and its dependencies
            self.assertFalse(model.Grade.select().where(model.Grade.grade == '1'))
            self.assertTrue(test_grade_2.delete_instance())
            self.assertTrue(test_subject_2.delete_instance())
            self.assertTrue(test_teacher.delete_instance())
            self.assertTrue(test_student.delete_instance())


class UserOperationsTest(unittest.TestCase):
    model.get_db().init('test_db.db')
    _student_template = {'first_name': 'test',
                         'last_name': 'test',
                         'group': 'test',
                         'username': hashpw('test_student'.encode('UTF-8'), gensalt()),
                         'password': 'test'}
    _teacher_template = {'first_name': 'test',
                         'last_name': 'test',
                         'username': 'test_teacher',
                         'password': 'test'}
    _table_model = [model.Student, model.Teacher, model.Subject, model.Grade, model.TeacherSubject]

    # FIXME: passing data to form
    def login_student(self, login, password):
        return self.client.post('/student_login/', follow_redirects=True, data=dict(
            username=login,
            password=password))

    def login_teacher(self, login, password):
        return self.client.post('/teacher_login/', follow_redirects=True, data=dict(
            username=login,
            password=password))

    def logout(self):
        return self.client.get('/logout/', follow_redirects=True)

    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        # model.get_db().create_tables(self._table_model)

    def tearDown(self):
        model.get_db().drop_tables(self._table_model, safe=True)

    # def test_correct_student_login_logout(self):
    #     with test_database(model.get_db(), [model.Student]):
    #         model.Student.create(**self._student_template)
    #         resp = self.login_student('test_student', 'test')  # correct username, correct password
    #         self.assertIn(b"<h1>Student\'s profile</h1>", resp.data)
    #         resp = self.logout()
    #         self.assertIn(b"<h1>Welcome</h1>", resp.data)

            # def test_incorrect_student_login(self):
            #     resp = self.login_student('atrawka', 'incorrect')  # correct username, incorrect password
            #     self.assertIn(b"Wrong password", resp.data)
            #     resp = self.login_student('incorrect', 'incorrect')  # incorrect username, incorrect password
            #     self.assertIn(b"Wrong username or password", resp.data)
            #
            # def test_correct_teacher_login_logout(self):
            #     resp = self.login_teacher('eunice', 'abc')  # correct username, correct password
            #     self.assertIn(b"<h1>Teacher\'s profile</h1>", resp.data)
            #     resp = self.logout()
            #     self.assertIn(b"<h1>Welcome</h1>", resp.data)
            #
            # def test_incorrect_teacher_login(self):
            #     resp = self.login_teacher('eunice', 'incorrect')  # correct username, incorrect password
            #     self.assertIn(b"Wrong password", resp.data)
            #     resp = self.login_teacher('incorrect', 'incorrect')  # incorrect username, incorrect password
            #     self.assertIn(b"Wrong username or password", resp.data)
            #
            # def test_get_current_user(self):
            #     with test_database(self.t_db, [db_model.Teacher]):
            #         test_teacher = Teacher.create(first_name='test',
            #                                       last_name='test',
            #                                       username='test_teacher',
            #                                       password=hashpw('test'.encode('utf-8'), gensalt()))
            #         with app.test_request_context():
            #             resp = self.login_teacher('test_teacher', 'test')
            #             authorize_teacher(test_teacher)
            #             self.assertIn(b"<h1>Teacher\'s profile</h1>", resp.data)
            #             self.assertEqual(get_current_user(), test_teacher)
            #
            # def test_guest_required(self):
            #     self.login_student('atrawka', 'abc')
            #     resp = self.client.get('/student_login/', follow_redirects=True)
            #     self.assertIn(b"<h1>Welcome</h1>", resp.data)
            #     resp = self.client.get('/logout/', follow_redirects=True)
            #     self.assertIn(b"<h1>Welcome</h1>", resp.data)


if __name__ == '__main__':
    unittest.main()
