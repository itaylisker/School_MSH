# TODO: add a variable to Grade that indicates the max amount of hours the grade can study per day (separate fridays from weekdays).
# TODO: add a variable to Teacher that indicates the max amount of hours the teacher can teach per day (separate fridays from weekdays).

class Subject:
    def __init__(self, name: str, max_hours_in_a_day: int):
        self.max_hours_in_a_day = max_hours_in_a_day
        self.name = name


class Teacher:

    def __init__(self, name: str, subject: Subject):
        self.name = name
        self.subject = subject.name
        # teachers don't work on hours that are marked as -1.
        # hours that are marked as 0 are hours when the teacher is teaching.
        # any other number is for priority reasons (1 higher priority than 2 ...)
        self.work_hours = [[2, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3]
                           for day in range(5)]
        self.work_hours.append([2, 1, 1, 1, 1, 2, 2, 3, -1, -1, -1, -1])  # friday work hours

    def cant_work(self, day, hour, flag):
        if flag == 1:
            for i in range(len(self.work_hours[day-1])):
                self.work_hours[day-1][i] = -1  # cant work at all
        else:
            self.work_hours[day-1][hour] = -1  # cant work at all

    def can_work(self, day, hour, flag):
        if flag == 1:
            for i in range(len(self.work_hours[day-1])):
                self.work_hours[day-1][i] = 1  # with the correct priority
        else:
            self.work_hours[day - 1][hour] = 1  # with the correct priority

    def is_working(self, day, hour, flag):
        if flag == 1:
            for i in range(len(self.work_hours[day-1])):
                self.work_hours[day-1][i] = 0  # is working
        else:
            self.work_hours[day - 1][hour] = 0  # is working


class Grade:

    def __init__(self, name: str, hours_per_subject: dict):
        self.name = name
        self.hours_per_subject = hours_per_subject
        self.MSH = []
        for day in range(5):  # Sunday through wednesday
            default_day_schedule = [None for hour in range(12)]  # hours 0 through 11
            self.MSH.append(default_day_schedule)
        self.MSH.append([None, None, None, None, None, None, None, None])

    def change_hour(self, teacher: Teacher, day: int, hour: int, action: str):

        if action.lower == "remove":
            self.hours_per_subject[self.MSH[day - 1][hour].subject] += 1
            teacher.work_hours[day - 1][hour] = 1  # priority
            self.MSH[day - 1][hour] = None

        elif action.lower == "add":
            self.MSH[day - 1][hour] = teacher
            self.hours_per_subject[teacher.subject] -= 1
            teacher.work_hours[day - 1][hour] = 0
        else:
            print('Invalid action')
        # if action.lower == "change":
        #     self.change_hour(teacher, day, hour, "remove")
        #     self.change_hour(teacher, day, hour, "add")



