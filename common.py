class Enum:
    LOGIN_INFO = 'login'
    SUCCESS = 'success'
    EXISTS = 'exists'
    ADD_SUBJECT = 'add_subject'
    GET_SUBJECTS = 'get_subjects'
    ADD_TEACHER = 'add_teacher'
    GET_TEACHERS = 'get_teachers'
    ADD_GRADE = 'add_grade'
    GET_GRADES = 'get_grades'
    ADD_CLASSROOM = 'add_classroom'
    GET_CLASSROOMS = 'get_classrooms'


class Classroom:
    def __init__(self, name: str, available: list[list[bool]]=None):
        self.name = name
        if available:
            self.available = available
        else:
            self.available = [[True for i in range(12)] for day in range(6)]


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
    def __init__(self, teacher: Teacher):
        self.teacher = teacher
        self.subject: str = teacher.subject
        self.hour: int = None
        self.day: int = None
        self.classroom: Classroom = None

    def assign(self, day, hour, classroom):
        self.hour = hour
        self.day = day
        self.classroom = classroom
        classroom.available[day][hour] = False


class Grade:

    def __init__(self, name: str, max_hours_per_day: int, max_hours_per_friday: int, hours_per_subject: dict[str: int]):  # dict consists of subject_name: hours_to_study_per_week
        self.name = name
        self.hours_per_subject = hours_per_subject
        self.MSH: list[list[Lesson]] = []
        for day in range(5):  # Sunday through wednesday
            default_day_schedule = [None for hour in range(max_hours_per_day)]  # hours 0 through 11
            self.MSH.append(default_day_schedule)
        self.MSH.append([None for i in range(max_hours_per_friday)])

    def change_hour(self, lesson: Lesson, day: int, hour: int, action: str):

        if action.lower() == "remove":
            self.hours_per_subject[self.MSH[day][hour].subject] += 1
            lesson.teacher.work_hours[day][hour] = True
            self.MSH[day][hour] = None
            lesson.classroom.available[day][hour] = True

        elif action.lower() == "add":
            self.MSH[day][hour] = lesson
            self.hours_per_subject[lesson.subject] = int(self.hours_per_subject[lesson.subject])-1
            lesson.teacher.work_hours[day][hour] = False
            lesson.classroom.available[day][hour] = False
        else:
            print('Invalid action')
        # if action.lower == "change":
        #     self.change_hour(teacher, day, hour, "remove")

        #     self.change_hour(teacher, day, hour, "add")


# TODO: think of an encryption that isn't hash
def encode_password(password):
    import hashlib
    return hashlib.md5(password.encode()).hexdigest()




classrooms = [Classroom("Room1"), Classroom("Room2")]
teachers = [Teacher("Teacher1", "Math", [[True] * 6 for _ in range(5)]), Teacher("Teacher2", "Science", [[True] * 6 for _ in range(5)])]
subjects = {"Math": Subject("Math", 2), "Science": Subject("Science", 2)}
grades = [Grade("Grade1", 6, 6, {"Math": 4, "Science": 2}), Grade("Grade2", 6, 6, {"Math": 4, "Science": 2})]





