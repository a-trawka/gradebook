from peewee import *
from gradebook import app

db_proxy = Proxy()

if app.config['DEBUG']:
    database = SqliteDatabase('gradebook.db')
elif app.config['TESTING']:
    database = SqliteDatabase('test_db.db')
else:
    print('#############################333333312321321')

db_proxy.initialize(database)


def get_db_proxy():
    return db_proxy


class BaseModel(Model):
    class Meta:
        database = db_proxy


class Subject(BaseModel):
    name = CharField(unique=True)

    def __repr__(self):
        return self.name


class Teacher(BaseModel):
    first_name = CharField()
    last_name = CharField()
    username = CharField(unique=True)
    password = CharField()

    def __repr__(self):
        return '{} {} - {}'.format(self.first_name, self.last_name, self.username)


class TeacherSubject(BaseModel):
    """TeacherSubject, in other words - specializations
    One teacher can teach many subjects,
    as well as one subject can be taught by many teachers.
    Many-to-many relationship model."""
    teacher = ForeignKeyField(Teacher, related_name='teachers')
    specialization = ForeignKeyField(Subject, related_name='specializations')

    def __repr__(self):
        return '{} taught by {}'.format(repr(self.specialization), repr(self.teacher))


class Student(BaseModel):
    first_name = CharField()
    last_name = CharField()
    group = CharField()
    username = CharField(unique=True)
    password = CharField()

    def __repr__(self):
        return '{} {}, group {} - {}'.format(self.first_name, self.last_name, self.group, self.username)


class Grade(BaseModel):
    student = ForeignKeyField(Student)
    subject = ForeignKeyField(Subject)
    teacher = ForeignKeyField(Teacher)
    grade = CharField()

    def __repr__(self):
        return 'student:{}, subject:{}, grade:{}, teacher:{}'.format(repr(self.student), repr(self.subject), self.grade, repr(self.teacher))

    class Meta:
        order_by = ('student', 'subject',)
