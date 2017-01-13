from peewee import *

db = SqliteDatabase('gradebook.db')

def get_db():
    return db

class BaseModel(Model):
    class Meta:
        database = db


class Subject(BaseModel):
    name = CharField()


class Teacher(BaseModel):
    first_name = CharField()
    last_name = CharField()
    username = CharField(unique=True)
    password = CharField()


class TeacherSubject(BaseModel):
    """TeacherSubject, in other words - specializations
    One teacher can teach many subjects,
    as well as one subject can be taught by many teachers.
    Many-to-many relationship model."""
    teacher = ForeignKeyField(Teacher, related_name='teachers')
    specialization = ForeignKeyField(Subject, related_name='specializations')


class Student(BaseModel):
    first_name = CharField()
    last_name = CharField()
    group = CharField()
    username = CharField(unique=True)
    password = CharField()


class Grade(BaseModel):
    student = ForeignKeyField(Student)
    subject = ForeignKeyField(Subject)
    teacher = ForeignKeyField(Teacher)
    grade = CharField()

    class Meta:
        order_by = ('student', 'subject',)
