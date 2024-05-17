from cryptography.fernet import Fernet


class Enum:

    ADMIN = 'admin'
    LOGIN_INFO = 'login'
    SUCCESS = 'success'
    FAIL = 'failure'
    EXISTS = 'exists'

    ADD_LESSONS = 'add_lessons'
    GET_LESSONS = 'get_lessons'

    ADD_SUBJECT = 'add_subject'
    GET_SUBJECTS = 'get_subjects'
    DELETE_SUBJECT = 'delete_subject'

    ADD_TEACHER = 'add_teacher'
    GET_TEACHERS = 'get_teachers'
    DELETE_TEACHER = 'delete_teacher'

    ADD_GRADE = 'add_grade'
    UPDATE_GRADES = 'update_grades'
    GET_GRADES = 'get_grades'
    DELETE_GRADE = 'delete_grade'

    ADD_CLASSROOM = 'add_classroom'
    GET_CLASSROOMS = 'get_classrooms'
    OPEN_SCHEDULE = 'open_schedule'


class Classroom:
    def __init__(self, name: str, available: list[list[bool]]=None):
        self.name = name
        if available:
            self.available = available
        else:
            self.available = [[True for hour in range(12)] for day in range(6)]


class Subject:
    def __init__(self, name: str, max_hours_in_a_day: int):
        self.name = name
        self.max_hours_in_a_day = max_hours_in_a_day


class Teacher:

    def __init__(self, name: str, subject: str, work_hours: list[list[bool]]):
        self.name = name
        self.subject = subject
        # if value is True than the teacher is available, if it's False the teacher is occupied
        self.work_hours = work_hours


class Lesson:
    def __init__(self, teacher: Teacher, classroom: Classroom = None, day: int = None, hour: int = None):
        self.teacher = teacher
        self.subject: str = teacher.subject
        self.hour: int = hour
        self.day: int = day
        self.classroom: Classroom = classroom

    def assign(self, day, hour, classroom):
        self.hour = hour
        self.day = day
        self.classroom = classroom


class Grade:

    def __init__(self, name: str, max_hours_per_day: int, max_hours_per_friday: int, hours_per_subject: dict[str: int]):  # dict consists of subject_name: hours_to_study_per_week
        self.name = name
        self.hours_per_subject = hours_per_subject
        self.max_hours_per_day = max_hours_per_day
        self.max_hours_per_friday = max_hours_per_friday
        self.schedule: list[list[Lesson]] = []
        for day in range(5):  # Sunday through wednesday
            default_day_schedule = [None for hour in range(max_hours_per_day)]  # hours 0 through 11
            self.schedule.append(default_day_schedule)
        self.schedule.append([None for i in range(max_hours_per_friday)])

    def change_hour(self, lesson: Lesson, action: str):

        if action.lower() == "remove":
            self.hours_per_subject[self.schedule[lesson.day][lesson.hour].subject] += 1
            lesson.teacher.work_hours[lesson.day][lesson.hour] = True
            self.schedule[lesson.day][lesson.hour] = None
            lesson.classroom.available[lesson.day][lesson.hour] = True

        elif action.lower() == "add":
            self.schedule[lesson.day][lesson.hour] = lesson
            lesson.teacher.work_hours[lesson.day][lesson.hour] = False
            lesson.classroom.available[lesson.day][lesson.hour] = False
        else:
            print('Invalid action')


def encode_password(password):
    import hashlib
    return hashlib.md5(password.encode()).hexdigest()


key = b'W8sEY6zLN2oMtz6HShYYwdL2sIU8gFm48bK7zYsTOI4='
cipher = Fernet(key)


def encrypt_message(message):
    return cipher.encrypt(message.encode())


def decrypt_message(encrypted_message):
    return cipher.decrypt(encrypted_message).decode()
