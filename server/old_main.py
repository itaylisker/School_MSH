from objects import Grade ,Teacher, Subject
import db_handle
hours_per_subject = {}
subjects_list = []
teachers_list = []
grades_list = []
DOW_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

add_or_stop_adding_subjects = int(input("if you want to add a teacher to the system press 1 else press 0"))
while add_or_stop_adding_subjects != 0 and add_or_stop_adding_subjects != 1:
    add_or_stop_adding_subjects = int(input("error, if you want to add a teacher to the system press 1 else press 0"))

while add_or_stop_adding_subjects != 0:
    subject_name = input("enter the teacher's name")
    subject_hours_in_a_day = int(input("enter the amount of hours that this subject can be taught in a single day: "))
    new_sub = Subject(subject_name.lower(), subject_hours_in_a_day)
    subjects_list.append(new_sub)

    add_or_stop_adding_subjects = int(input("if you want to add a teacher to the system press 1 else press 0"))
    while add_or_stop_adding_subjects != 0 and add_or_stop_adding_subjects != 1:
        add_or_stop_adding_subjects = int(input("error, if you want to add a teacher to the system press 1 else press 0"))

add_or_stop_adding_teachers = int(input("if you want to add a teacher to the system press 1 else press 0"))
while add_or_stop_adding_teachers != 0 and add_or_stop_adding_teachers != 1:
    add_or_stop_adding_teachers = int(input("error, if you want to add a teacher to the system press 1 else press 0"))

while add_or_stop_adding_teachers != 0:
    teacher_name = input("enter the teacher's name")
    teacher_subject = input("enter the teacher's subject")
    new_t = Teacher(teacher_name.lower(), [i for i in subjects_list if i.name == teacher_subject.lower][0].name)
    teachers_list.append(new_t)

    for i in DOW_list:

        while True:
            hour_cant_work = int(input(f"enter an hour that you cant work on {i} if you cant work in this day enter -2, if you finished entering hours press -1"))

            while -3 < hour_cant_work < 12:
                hour_cant_work = input(f"error, enter an hour that you cant work on {i} if you cant work in this day enter -1, if you finished entering hours press -2")
            if hour_cant_work == -1:
                break
                # stop loop
            elif hour_cant_work == -2:
                new_t.cant_work(DOW_list.index(i), 0, 1)
                # delete all day
            else:
                new_t.cant_work(DOW_list.index(i), hour_cant_work, 0)
                # delete specific hour

    add_or_stop_adding_teachers = int(input("if you want to add a teacher to the system press 1 else press 0"))
    while add_or_stop_adding_teachers != 0 and add_or_stop_adding_teachers != 1:
        add_or_stop_adding_teachers = int(input("error, if you want to add a teacher to the system press 1 else press 0"))


# --------------------------------------------------------------------------------------------------------------------------------


for i in subjects_list:
    hours_per_subject[i.name] = 0

add_or_stop_adding_grades = int(input("if you want to add a grade to the system press 1 else press 0"))

while add_or_stop_adding_grades != 0 and add_or_stop_adding_grades != 1:
    add_or_stop_adding_grades = int(input("error, if you want to add a grade to the system press 1 else press 0"))

while add_or_stop_adding_grades != 0:
    grade_name = input("enter the grade")

    for i in hours_per_subject.keys():
        hours_for_subject = int(input(f"enter amount of hours per week that {grade_name} needs to study {i}: "))

        while hours_for_subject < 0 or hours_for_subject > 81:  # 81 is the amount of hours in a school week
            if hours_for_subject + sum(hours_per_subject.values()) > 81:
                hours_for_subject = int(input(f"amount of hours exceeds the max amount you can study in a week! please try again: "))
            else:
                hours_for_subject = int(input(f"input was invalid, please try again: "))
        hours_per_subject[i] = hours_for_subject

    new_g = Grade(grade_name, hours_per_subject)
    grades_list.append(new_g)

    add_or_stop_adding_grades = int(input("if you want to add a grade to the system press 1 else press 0"))
    while add_or_stop_adding_grades != 0 and add_or_stop_adding_grades != 1:
        add_or_stop_adding_grades = int(input("error, if you want to add a grade to the system press 1 else press 0"))

# start of MSH building ⤵⤵⤵⤵⤵⤵⤵ MSH = Maarehet SHaot (NOT a schedule!!!)
# TODO: build MSH grade by grade for every day (sunday schedule for every grade then monday schedule for every grade...)
for grade in grades_list:

    for i in range(1, 7):  # build MSH day by day for every grade (every day for grade x then every day for grade y etc...)

        for subject in hours_per_subject:
            hour = 0  # counter for current lesson tracking
            same_subject_in_a_day = 0  # counter for max lessons of a specific subject in a single day

            while hours_per_subject[subject] > 0 and same_subject_in_a_day < [j for j in subjects_list if j.name == subject.name][0].max_hours_in_a_day:
                hour += 1
                same_subject_in_a_day += 1
                available_teachers_of_subject = [j for j in teachers_list if j.subject == subject.name and j.work_hours[i][hour] > 0]

                for j in available_teachers_of_subject:
                    if j.work_hours[i][hour] > 0:
                        grades_list[grades_list.index(grade)].change_hour(teachers_list[teachers_list.index(j)], i, hour, 'add')
                        break
