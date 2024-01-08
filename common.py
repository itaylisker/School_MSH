class Enum:
    LOGIN_INFO = 'login'
    CREATE_SCHEDULES = 'create_schedules'
    SUCCESS = 'success'
    EXISTS = 'exists'
    ADD_SUBJECT = 'add_subject'
    GET_SUBJECTS = 'get_subjects'
    ADD_TEACHER = 'add_teacher'
    GET_TEACHERS = 'get_teachers'
    ADD_GRADE = 'add_grade'
    GET_GRADES = 'get_grades'
    ADD_CLASSROOM = 'add_classroom'


class Classroom:
    def __init__(self, name: str, hours_per_day: int, hours_per_friday: int):
        self.name = name
        self.available: list[list[bool]] = [[True for i in range(hours_per_day)] for day in range(5)]
        self.available.append([True for i in range(hours_per_friday)])


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
    # TODO: rewrite this ⬇
    def cant_work(self, day, hour, flag):
        if flag == 1:
            for i in range(len(self.work_hours[day-1])):
                self.work_hours[day-1][i] = False  # cant work at all
        else:
            self.work_hours[day-1][hour] = False  # cant work at all

    def can_work(self, day, hour, flag):
        if flag == 1:
            for i in range(len(self.work_hours[day-1])):
                self.work_hours[day-1][i] = True  # with the correct priority
        else:
            self.work_hours[day - 1][hour] = True  # with the correct priority

    def is_working(self, day, hour, flag):
        if flag == 1:
            for i in range(len(self.work_hours[day-1])):
                self.work_hours[day-1][i] = False  # is working
        else:
            self.work_hours[day - 1][hour] = False  # is working


class Lesson:
    def __init__(self, hour: int, day: int, room: Classroom, teacher: Teacher):
        self.hour = hour
        self.day = day
        self.room = room
        self.teacher = teacher
        self.subject = teacher.subject
        room.available[day][hour] = False


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

        if action.lower == "remove":
            self.hours_per_subject[self.MSH[day - 1][hour].subject] += 1
            lesson.teacher.work_hours[day - 1][hour] = True
            self.MSH[day - 1][hour] = None
            lesson.room.available[day][hour] = True

        elif action.lower == "add":
            self.MSH[day - 1][hour] = lesson
            self.hours_per_subject[lesson.subject] -= 1
            lesson.teacher.work_hours[day - 1][hour] = False
            lesson.room.available[day][hour] = False
        else:
            print('Invalid action')
        # if action.lower == "change":
        #     self.change_hour(teacher, day, hour, "remove")

        #     self.change_hour(teacher, day, hour, "add")


# TODO: think of an encryption that isn't hash
def encode_password(password):
    import hashlib
    return hashlib.md5(password.encode()).hexdigest()
