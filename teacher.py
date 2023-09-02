class Teacher:
    import subject

    def __init__(self, name: str, subject: subject):
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

    # def print_teacher_work_hours(self):
    #     for i in range(len(self.work_hours)):
    #         if i == 0:
    #             print("Sunday:\n")
    #         elif i == 1:
    #             print("Monday:\n")
    #         elif i == 2:
    #             print("Tuesday:\n")
    #         elif i == 3:
    #             print("Wednesday:\n")
    #         elif i == 4:
    #             print("Thursday:\n")
    #         else:
    #             print("Friday:\n")
    #
    #         for j in range(len(self.work_hours[i])):
    #             print("hour ", j, ":")
    #             if self.work_hours[j] == -1:
    #                 print("can't work")
    #             elif self.work_hours[j] == 0:
    #                 print("working")
    #             else:
    #                 print("available for work")
