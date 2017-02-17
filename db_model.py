from peewee import *

db = SqliteDatabase('gradebook.db')


def get_db():
    return db


class BaseModel(Model):
    class Meta:
        database = db


class Subject(BaseModel):
    def __repr__(self):
        return self.name

    name = CharField()


class Teacher(BaseModel):
    def __repr__(self):
        return '{} {} - {}'.format(self.first_name, self.last_name, self.username)

    first_name = CharField()
    last_name = CharField()
    username = CharField(unique=True)
    password = CharField()


class TeacherSubject(BaseModel):
    """TeacherSubject, in other words - specializations
    One teacher can teach many subjects,
    as well as one subject can be taught by many teachers.
    Many-to-many relationship model."""
    def __repr__(self):
        return '{} taught by {}'.format(repr(self.specialization), repr(self.teacher))

    teacher = ForeignKeyField(Teacher, related_name='teachers')
    specialization = ForeignKeyField(Subject, related_name='specializations')


class Student(BaseModel):
    def __repr__(self):
        return '{} {}, group {} - {}'.format(self.first_name, self.last_name, self.group, self.username)

    first_name = CharField()
    last_name = CharField()
    group = CharField()
    username = CharField(unique=True)
    password = CharField()


class Grade(BaseModel):
    def __repr__(self):
        return 'student:{}, subject:{}, grade:{}, teacher:{}'.format(repr(self.student), repr(self.subject), self.grade, repr(self.teacher))

    student = ForeignKeyField(Student)
    subject = ForeignKeyField(Subject)
    teacher = ForeignKeyField(Teacher)
    grade = CharField()

    class Meta:
        order_by = ('student', 'subject',)
