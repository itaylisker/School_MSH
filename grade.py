class Grade:
    import teacher

    def __init__(self, name: str, hours_per_subject: dict):
        self.name = name
        self.hours_per_subject = hours_per_subject
        self.MSH = []
        for day in range(5):  # Sunday through wednesday
            default_day_schedule = [None for hour in range(12)]  # hours 0 through 11
            self.MSH.append(default_day_schedule)
        self.MSH.append([None, None, None, None, None, None, None, None])

    def change_hour(self, teacher: teacher, day: int, hour: int, action: str):

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
