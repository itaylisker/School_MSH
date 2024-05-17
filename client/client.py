from tkinter import messagebox
from common import Teacher, Grade, Subject, Classroom, Lesson, Enum, encrypt_message, decrypt_message
import windows
import socket
import json

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5050))


def close_connection(window):

    """
    :param window: closes the application --> windows.LoginWindow / windows.MainApplication
    :return: destroys the window and closes the connection
    """

    print("Closing", type(window))
    window.destroy()
    client_socket.close()


# Function to check login credentials
def check_credentials(window, username_entry, password_entry):

    """
    :param window: the login window --> window.LoginWindow
    :param username_entry: the username entry --> tkinter.Entry
    :param password_entry: the password entry --> tkinter.Entry
    :return: if credentials are correct, opens main application. shows messagebox for each case(wrong password, empty fields...)
    """

    print("Checking", type(username_entry))
    username = username_entry.get()
    password = password_entry.get()
    credentials = f'{Enum.LOGIN_INFO},{username},{password}'
    print('credentialssssssssssssssssss:', encrypt_message(credentials), decrypt_message(encrypt_message(credentials)))
    client_socket.send(encrypt_message(credentials))
    cred_check = decrypt_message(client_socket.recv(4096))
    print('cred_checkkkkkkkkkkkkkk: ', cred_check)
    if cred_check == Enum.ADMIN:
        windows.MainApplication()
        window.destroy()
    elif cred_check == 'Invalid username':
        messagebox.showerror("login failed", "Username Doesn't Exist")
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
    elif cred_check == 'one or more of the fields are empty':
        messagebox.showerror("login failed", "One Or More Of The Fields Are Empty")
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
    else:
        messagebox.showerror("login failed", "Wrong Password")
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')


def create_schedules(grades, subjects):
    """

    :param grades: Dict of grades from database --> dict{grade_id: common.Grade}
    :param subjects: Dict of subjects from database --> dict{subject_id: common.Subject}
    :return: creates schedules for all the registered classes('grades') and updates corresponding values in database.
     raises messagebox.showerror if there aren't enough teachers with what teachers are missing
    """
    teachers = get_teachers(original=True)
    classrooms = get_classrooms(original=True)
    if not grades:
        grades = get_grades()
    if not subjects:
        subjects = get_subjects()

    trys = 0
    scheduled_lessons_dict: dict[Lesson: Grade] = {}  # dict of assigned lessons (for while condition) -> [Lesson_object: Grade_object,...]
    subjects_lacking_in_teachers = []
    teaching_dict = {}
    # create a dictionary that states which teacher is teaching what class {(grade.name, subject): teacher.name}
    for grade in grades.values():
        for subject in grade.hours_per_subject.keys():
            tup_to_add = (grade.name, subject)
            teaching_dict[tup_to_add] = None

    #print(f'{teachers}\n{grades}\n{classrooms}\n{subjects}')
    #print('$$$$$$$$$$$$$$$$$$$$$',grades[5].name,grades[5].hours_per_subject)
    #print([teacher.work_hours for teacher in teachers.values() if teacher.name == 'Ido Kedem'])

    def check_if_enough_hours(subject):

        hours_of_subject_for_grades = [(grade.name, int(grade.hours_per_subject[subject]), print('##################', grade.name, grade.hours_per_subject)) for grade in grades.values() if subject in grade.hours_per_subject]
        sorted_hours_of_subject_for_grades = sorted(hours_of_subject_for_grades, key=lambda x: x[1])

        sorted_teachers_of_subject = sorted([[teacher.name, sum([sum(day) for day in teacher.work_hours])] for teacher in teachers.values() if teacher.subject == subject], key=lambda x: x[1])
        #print('||||||||||||||||||||||||||||||', sorted_teachers_of_subject,'\n',subject)
        for grade_hours in sorted_hours_of_subject_for_grades:

            grade_name = grade_hours[0]
            grade_hours_of_subject = grade_hours[1]
            #print('!!!!!!!!!!!!',grade_name, grade_hours_of_subject)
            for index, teacher_hours in enumerate(sorted_teachers_of_subject):

                teacher_name = teacher_hours[0]
                teacher_hours_of_subject = teacher_hours[1]
                #print('@@@@@@@@@@@@@@@@@@@@',teacher_name, teacher_hours_of_subject)
                if teacher_hours_of_subject >= grade_hours_of_subject:
                    teaching_dict[(grade_name, subject)] = teacher_name
                    sorted_teachers_of_subject[index][1] -= grade_hours_of_subject
                    grade_hours_of_subject = 0
                    break
            if grade_hours_of_subject != 0:
                subjects_lacking_in_teachers.append(subject)
        return subjects_lacking_in_teachers

    for subject in subjects.values():
        print(check_if_enough_hours(subject.name))

        if len(subjects_lacking_in_teachers) > 0:
            messagebox.showerror(
                "not enough staff",
                f"not enough teachers for subjects: {','.join(subjects_lacking_in_teachers)} "
            )

            return
    #print(teaching_dict)
    adjusted_teachers_dict = {teacher.name: teacher for teacher in teachers.values()}
    adjusted_grades_dict = {grade.name: grade for grade in grades.values()}
    adjusted_classrooms_dict = {classroom.name: classroom for classroom in classrooms.values()}
    adjusted_subjects_dict = {subject.name: subject for subject_id, subject in subjects.items()}

    #print(f'{adjusted_teachers_dict}\n{adjusted_grades_dict}\n{adjusted_classrooms_dict}\n{adjusted_subjects_dict}')

    missing_periods = []

    def find_available_subject(grade_object, day, hour):
        # Find a teacher who teaches the subject, teaches the given class and is available at the given day and hour
        available_teachers = []
        subjects_of_grade_dict = {grade_and_subject_tup: teacher_name for grade_and_subject_tup, teacher_name in teaching_dict.items() if grade_and_subject_tup[0] == grade_object.name}
        #print('SUBS', subjects_of_grade_dict)

        for grade_and_subject_tup, teacher_name in subjects_of_grade_dict.items():

            teacher = [teacher for teacher in adjusted_teachers_dict.values() if teacher.name == teacher_name][0]
            subject_instances_scheduled = [lesson for lesson, grade in scheduled_lessons_dict.items()
                         if lesson.subject == teacher.subject and grade.name == grade_object.name]
            is_teacher_available = [lesson for lesson in scheduled_lessons_dict.keys()
                                    if lesson.day == day and lesson.hour == hour and lesson.teacher == teacher]
            max_in_a_day = adjusted_subjects_dict[teacher.subject].max_hours_in_a_day
            required_per_week = grade_object.hours_per_subject[teacher.subject]
            #print(len(teacher.work_hours[day]), hour, len(subject_instances_scheduled), required_per_week)
            if (((len(teacher.work_hours[day]) > hour) and is_teacher_available == []
                    and
                    len(subject_instances_scheduled) < int(required_per_week))
                    and
                    len([lesson for lesson in subject_instances_scheduled if lesson.day == day]) < max_in_a_day):
                available_teachers.append(teacher)
        return available_teachers

    def find_available_classroom(grade_name, day, hour):
        # Find a classroom that is available at the given day and hour
        if adjusted_classrooms_dict[grade_name].available[day][hour]:
            return adjusted_classrooms_dict[grade_name]
        for classroom in adjusted_classrooms_dict.values():
            if classroom.available[day][hour]:
                return classroom
        return None

    def schedule_lesson(grade, teacher, classroom, day, hour):
        lesson = Lesson(teacher)
        lesson.assign(day, hour, classroom)
        grade.change_hour(lesson, day, hour, "add")

    '''while not solution: 
    build lesson blocks, after having all lessons start inserting them with algorithm,
    a while with two for loops, brute force through every option until you get a solution.
    while condition: while "teaching dict" is not empty. the dict contains all of the lessons that should exist in the schedule, 
    when it empty's them all out, they have all been scheduled successfully.
    when its empty use the "schedule lesson" function to schedule the lessons.
    alternative: make another dict to keep track of scheduled lessons instead of removing them from the "teaching dict" dict
     and make the while condition depend on the length of the new dict, if its length is the same as "teaching dict" it stops.'''

    while (len(scheduled_lessons_dict) != len(teaching_dict)): #and trys == 0:
        #trys += 1
        for grade in adjusted_grades_dict.values():
            for day in range(6):
                if day == 5:
                    hours_to_schedule = grade.max_hours_per_friday
                else:
                    hours_to_schedule = grade.max_hours_per_day
                for hour in range(hours_to_schedule):
                    room_of_lesson = find_available_classroom(grade.name, day, hour)
                    possible_subjects_of_lesson = find_available_subject(grade, day, hour)
                    if len(possible_subjects_of_lesson) == 0:
                        #print('!@#$%^&*()!@#$%^&*()!@#$%^&*()_!@#$%^&*()_, NO AVAILABLE TEACHER')
                        missing_periods.append((day,hour,grade.name))
                        continue
                    if hour != 0:
                        todays_lessons = [lesson for lesson in scheduled_lessons_dict.keys() if lesson.day == day]
                        previous_lesson_subject = [lesson.subject for lesson in todays_lessons if lesson.hour == hour-1][0]

                        times_previous_lesson_appeared_today = sum(
                            [1 for lesson in todays_lessons if lesson.subject == previous_lesson_subject]
                        )

                        if (
                                times_previous_lesson_appeared_today < adjusted_subjects_dict[previous_lesson_subject].max_hours_in_a_day
                                and previous_lesson_subject in [teacher.subject for teacher in possible_subjects_of_lesson]
                        ):
                              teacher_of_lesson = [teacher for teacher in possible_subjects_of_lesson
                                                 if teacher.subject == previous_lesson_subject
                                                ][0]
                        else:
                            teacher_of_lesson = [teacher for teacher in possible_subjects_of_lesson][0]
                    else:
                        teacher_of_lesson = [teacher for teacher in possible_subjects_of_lesson][0]
                    scheduled_lessons_dict[Lesson(teacher_of_lesson, room_of_lesson, day, hour)] = grade
                    #print('SCHEDULED LESSON!!!!!!!!!!!!', teacher_of_lesson.name, room_of_lesson.name, day, hour, grade.name)
        #print('END OF WHILE', trys, missing_periods)
    #print(missing_periods)

    for lesson, grade in scheduled_lessons_dict.items():

        adjusted_grades_dict[grade.name].change_hour(lesson, 'add')

    #print([[[hour.subject if hour else None for hour in day] for day in schedule] for schedule in
           #[grade.schedule for grade in adjusted_grades_dict.values()]])
    #print(grades)
    #print(adjusted_grades_dict)
    #print("missing::::::", missing_periods)
    #for teacher in adjusted_teachers_dict.values():
        #print(teacher.work_hours)
        #print('checlklhsbdfbvlkjnsdf;jbhsd;ibsg;ijbr',teacher.name, sum(1 for lesson in scheduled_lessons_dict if lesson.teacher.name == teacher.name), sum([sum([1 for hour in day]) for day in teacher.work_hours]))

    formated_lessons_list = []
    changed_teachers = {}
    changed_classrooms = {}
    users = get_teachers()
    for lesson, scheduled_grade in scheduled_lessons_dict.items():
        hour = lesson.hour
        day = lesson.day
        classroom_id = [cid for cid, classroom in classrooms.items() if classroom.name == lesson.classroom.name][0]
        teacher_id = [tid for tid, teacher in users.items() if teacher.name == lesson.teacher.name][0]
        grade_id = [gid for gid, grade in grades.items() if grade.name == scheduled_grade.name][0]
        changed_teachers[teacher_id] = lesson.teacher.work_hours
        changed_classrooms[classroom_id] = lesson.classroom.available
        #print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&',grade_id,teacher_id,classroom_id)
        #if teacher_id == 10:
            #pass
        formated_lessons_list.append((hour, day, classroom_id, teacher_id, grade_id))

    lessons_and_changes = f'{json.dumps(formated_lessons_list)}|{json.dumps(changed_teachers)}|{json.dumps(changed_classrooms)}'
    file_size = str(len(encrypt_message(lessons_and_changes)))
    size_text = f'{Enum.ADD_LESSONS},{file_size}'
    client_socket.send(encrypt_message(size_text))


    #print('poiuytyuiopoiuytrtyuiopoiuytyuiopoiuytyuio', lessons_and_changes)
    client_socket.send(encrypt_message(lessons_and_changes))
    if decrypt_message(client_socket.recv(4096)) == Enum.SUCCESS:
        messagebox.showinfo('Schedule status', 'Schedules created successfully!')
    return grades


def add_subject(subject_name_entry, max_hours_entry, window, parent, subjects):
    """

    :param subject_name_entry: subject name entry --> tk.Entry
    :param max_hours_entry: max hours the subject can be studied entry in a day --> tk.Entry
    :param window: add_subject frame --> tk.Frame
    :param parent: main application window --> windows.MainApplication
    :param subjects: subjects: Dict of subjects from database --> dict{subject_id: common.Subject}
    :return: adds subject to database and 'subjects' dict.
    raises messagebox.showerror if subject exists or if not all fields are filled
    """
    subject_name = subject_name_entry.get().title()
    max_hours = int(max_hours_entry.get())

    if not (subject_name and max_hours):
        messagebox.showerror("Input Error", "Both Fields Must Be Filled.")
    else:
        subject = f'{Enum.ADD_SUBJECT},{subject_name},{max_hours}'
        client_socket.send(encrypt_message(subject))
        response = decrypt_message(client_socket.recv(4096))
        if response == Enum.EXISTS:
            messagebox.showerror("Input Error", "Subject Already Exists.")
            subject_name_entry.delete(0, 'end')
            max_hours_entry.delete(0, 'end')
        else:

            if type(subjects) != dict:
                subjects = {}
            subjects[int(response)] = Subject(subject_name, max_hours)

            messagebox.showinfo('successfully added', 'Subject Added Successfully')
            window.destroy()
            parent.create_main_app_frame()


def get_subjects():
    """

    :return: Dict of all the subjects in the database --> dict{subject_id: common.Subject}
    """
    client_socket.send(encrypt_message(f'{Enum.GET_SUBJECTS}'))
    file_size = decrypt_message(client_socket.recv(4096))
    if file_size == 'no subjects found':
        messagebox.showerror("Input Error", "There are no subjects in the system")
        return 'no subjects found'
    else:
        subjects = json.loads(decrypt_message(client_socket.recv(int(file_size))))  # Convert json string to list[list]
        subjects_dict = {}
        for subject in subjects:
            subjects_dict[subject[0]] = Subject(subject[1], subject[2])
        return subjects_dict


def delete_subject(subject_id, subject_name, window, parent, grades, subjects, grades_to_change=None):
    """

    :param subject_id: id of the subject to delete --> int
    :param subject_name: name of the subject to delete --> str
    :param window: delete_subject_frame --> windows.DeleteSubjectFrame
    :param parent: main application --> Windows.MainApplication
    :param grades: Dict of grades from database --> dict{grade_id: common.Grade}
    :param subjects: Dict of subjects from database --> dict{subject_id: common.Subject}
    :param grades_to_change: the grades where the hours_per_subject dict should be changed --> list[garde_id --> int]
    :return: deletes the subject from the database and updates the grades accordingly.
    also updates the 'grades' and 'subjects' dicts accordingly and then destroys the frame and opens the main application frame.
    """
    client_socket.send(encrypt_message(f'{Enum.DELETE_SUBJECT},{subject_id}'))
    response = decrypt_message(client_socket.recv(4096))
    if response == Enum.SUCCESS:
        print('got hereeeeeeeeeeeee', subjects[subject_id])
        del subjects[subject_id]
        if grades_to_change:
            print('whattttttttttttttttttttttttttttttttttttttttt', grades_to_change)
            dicts_to_change = {}
            for grade_id in grades_to_change:
                dicts_to_change[grade_id] = grades[grade_id].hours_per_subject
            print(dicts_to_change)
            file_size = str(len(encrypt_message(json.dumps(dicts_to_change))))
            client_socket.send(encrypt_message(f'{Enum.UPDATE_GRADES},{file_size}'))
            client_socket.send(encrypt_message(json.dumps(dicts_to_change)))
            response = decrypt_message(client_socket.recv(4096))
        if response == Enum.SUCCESS:
            print('ain\'t now wayyyyyyyyyyyyyyy')
            for grade_id in grades_to_change:
                print(grades[grade_id].hours_per_subject[subject_name])
                del grades[grade_id].hours_per_subject[subject_name]
            messagebox.showinfo('Successfully deleted', 'Subject deleted successfully')
            window.destroy()
            parent.create_main_app_frame()


def add_teacher(
        teacher_name_entry, teacher_password_entry,
        teacher_subject_id, teacher_day_off_number,
        teacher_max_hours_day_entry, teacher_max_hours_friday_entry,
        window, parent, teachers, subjects
                ):
    """

    :param teacher_name_entry:  teacher name entry --> tk.Entry
    :param teacher_password_entry: teacher password entry --> tk.Entry
    :param teacher_subject_id: id of teacher's subject --> int
    :param teacher_day_off_number: number that represents the teacher's day off --> int
    :param teacher_max_hours_day_entry: max hours the teacher can work in a weekday entry --> tk.Entry
    :param teacher_max_hours_friday_entry: max hours the teacher can work in a friday entry --> tk.Entry
    :param window: add_teacher_frame --> windows.AddTeacherFrame
    :param parent:main application --> Windows.MainApplication
    :param teachers: Dict of teachers from database --> dict{teacher_id: common.Teacher}
    :param subjects: Dict of subjects from database --> dict{subject_id: common.Subject}
    :return: adds teacher to database and to 'teachers' dict.
    raises messagebox.showerror if teacher exists or if not all fields are filled.
    """
    teacher_name = teacher_name_entry.get().title()
    teacher_day_off = teacher_day_off_number+1
    teacher_max_hours_day = int(teacher_max_hours_day_entry.get())
    teacher_max_hours_friday = int(teacher_max_hours_friday_entry.get())

    print(f'''{teacher_name} , 
                    {teacher_subject_id} , 
                    {teacher_day_off} , 
                    {teacher_max_hours_day} , 
                    {teacher_max_hours_friday}''')

    if not (teacher_name and teacher_subject_id and teacher_day_off and teacher_max_hours_day and teacher_max_hours_friday):
        messagebox.showerror("Input Error", "All fields must be filled.")

    else:
        teacher = f'{Enum.ADD_TEACHER},{teacher_name},{teacher_subject_id},{teacher_day_off},{teacher_max_hours_day},{teacher_max_hours_friday},{teacher_password_entry.get()}'
        client_socket.send(encrypt_message(teacher))
        response = decrypt_message(client_socket.recv(4096))
        if response == Enum.EXISTS:
            messagebox.showerror("Input Error", "Teacher With This Name already exists.")
        else:
            data = teacher.split(',')
            work_hours = [[True for i in range(int(data[4]))] for day in range(5)]
            work_hours.append([True for i in range(int(data[5]))])
            work_hours[int(data[3]) - 1] = [False for i in range(len(work_hours[int(data[3]) - 1]))]
            try:
                if type(teachers) != dict:
                    teachers = {}
                teachers[int(response)] = Teacher(teacher_name, subjects[teacher_subject_id].name, work_hours)
            finally:
                messagebox.showinfo('successfully added', 'Teacher Added Successfully')
                window.destroy()
                parent.create_main_app_frame()


def get_teachers(original=False):
    """

    :param original: flag indicating if should get original teachers or scheduled teachers --> bool
    :return: dict of all the teachers from database --> dict{teacher_id: common.Teacher}
    """
    if original:
        client_socket.send(encrypt_message(f'{Enum.GET_TEACHERS},True'))
    else:
        client_socket.send(encrypt_message(f'{Enum.GET_TEACHERS}'))
    file_size = decrypt_message(client_socket.recv(4096))
    if file_size == 'no teachers found':
        messagebox.showerror("Input Error", "There Are No Teachers In The System")
        return 'no teachers found'
    else:
        teachers = json.loads(decrypt_message(client_socket.recv(int(file_size))))  # Convert json string to list[list]
        teachers_dict = {}
        if original:
            for teacher in teachers:
                print(teacher)
                teachers_dict[teacher[0]] = Teacher(teacher[1], teacher[-1], teacher[-2])
                print('originalllllllllll',teachers_dict[teacher[0]].name)
        else:
            for teacher in teachers:
                teachers_dict[teacher[0]] = Teacher(teacher[1], teacher[-1], teacher[4])
                print('not originalllllllllll',teachers_dict[teacher[0]].name)
        return teachers_dict


def delete_teacher(teacher_id, teacher_name, window, parent, teachers):
    """

    :param teacher_id: id of the teacher to delete --> int
    :param teacher_name: name of the teacher to delete --> str
    :param window: delete_teacher_frame --> windows.DeleteTeacherFrame
    :param parent: main application --> Windows.MainApplication
    :param teachers: Dict of teachers from database --> dict{teacher_id: common.Teacher}
    :return: deletes the teacher from the database.
    also updates the 'teachers' dict accordingly and then destroys the frame and opens the main application frame.
    """
    client_socket.send(encrypt_message(f'{Enum.DELETE_TEACHER},{teacher_name}'))
    response = decrypt_message(client_socket.recv(4096))
    if response == Enum.SUCCESS:
        del teachers[teacher_id]
        messagebox.showinfo('Successfully deleted', 'Teacher deleted successfully')
        window.destroy()
        parent.create_main_app_frame()


def add_grade(grade_name_entry, max_hours_day, max_hours_friday, hours_per_subject_dict, window, parent, grades, classrooms):
    """

    :param grade_name_entry: grade name entry --> tk.Entry
    :param max_hours_day: max hours the class('grade') can study in a weekday --> tk.Entry
    :param max_hours_friday: max hours the class('grade') can study in a friday --> tk.Entry
    :param hours_per_subject_dict: hours the class('grade') needs to study of each subject in a week --> dict{subject_name: int}
    :param window: add_grade_frame --> windows.AddGradeFrame
    :param parent: main application --> Windows.MainApplication
    :param grades: Dict of grades from database --> dict{grade_id: common.Grade}
    :param classrooms: Dict of classrooms from database --> dict{classroom_id: common.Classroom}
    :return: adds grade to database and to 'grades' dict. adds classroom named {grade_name} to database ant to 'classrooms' dict.
    raises messagebox.showerror if grade exists or if not all fields are filled.
    """
    grade_name = grade_name_entry.get().title()
    max_hours_day = int(max_hours_day.get())
    max_hours_friday = int(max_hours_friday.get())
    file_size = str(len(encrypt_message(json.dumps(hours_per_subject_dict))))
    size_text = f'{Enum.ADD_GRADE},{file_size}'
    client_socket.send(encrypt_message(size_text))
    grade = f'{grade_name}|{max_hours_day}|{max_hours_friday}|{json.dumps(hours_per_subject_dict)}'
    client_socket.send(encrypt_message(grade))
    response = decrypt_message(client_socket.recv(4096))
    if response == Enum.EXISTS:
        messagebox.showerror("Input error", "Grade with this name already exists.")
        window.destroy()
        parent.deiconify()
    else:
        print(response, type(response))
        response = json.loads(response)
        print(response, type(response))
        available = [
            [True, True, True, True, True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True, True, True, True, True],
            [True, True, True, True, True, True, True, True, True, True, True]
        ]
        if type(grades) != dict:
            grades = {}
        if type(classrooms) != dict:
            classrooms = {}

        grades[response[0]] = Grade(grade_name, max_hours_day, max_hours_friday, hours_per_subject_dict)
        classrooms[response[1]] = Classroom(grade_name, available)
        messagebox.showinfo('Successfully added', 'Grade added successfully')


def get_grades():
    """

    :return: dict of all grades from database --> dict{grade_id: common.Grade}
    """
    client_socket.send(encrypt_message(Enum.GET_GRADES))
    file_size = decrypt_message(client_socket.recv(4096))
    if file_size == 'no grades found':
        messagebox.showerror("Input Error", "There Are No Grades In The System")
        return 'no grades found'
    else:
        grades = json.loads(decrypt_message(client_socket.recv(int(file_size))))  # Convert json string to list[list]
        grades_dict = {}
        for grade in grades:
            hours_per_subject = {subject_name.title(): int(hours) for subject_name, hours in grade[2].items()}
            grades_dict[grade[0]] = Grade(grade[1], grade[3], grade[4], hours_per_subject)
        return grades_dict


def delete_grade(grade_id, grade_name, classroom_id, window, parent, grades, classrooms):
    """

    :param grade_id: id of grade to delete --> int
    :param grade_name: name of grade to delete --> str
    :param classroom_id: id of classroom of grade to delete --> int
    :param window: delete_grade_frame --> windows.DeleteGradeFrame
    :param parent: main application --> Windows.MainApplication
    :param grades: Dict of grades from database --> dict{grade_id: common.Grade}
    :param classrooms: Dict of classrooms from database --> dict{classroom_id: common.Classroom}
    :return:deletes the grade and classroom of grade from the database.
    also updates the 'grades' and 'classrooms' dicts accordingly and then destroys the frame and opens the main application frame.
    """
    client_socket.send(encrypt_message(f'{Enum.DELETE_GRADE},{grade_name}'))
    print('sent')
    response = decrypt_message(client_socket.recv(4096))
    print('received')
    if response == Enum.SUCCESS:
        print('successfully')
        print(grades[grade_id], classrooms[[classroom_id for classroom_id, classroom in classrooms.items() if classroom.name == grade_name][0]])
        del grades[grade_id]
        del classrooms[classroom_id]
        messagebox.showinfo('Successfully deleted', 'Grade deleted successfully')
        window.destroy()
        parent.create_main_app_frame()


def get_classrooms(original=False):
    """

    :param original: flag indicating if should get original classrooms or scheduled classrooms --> bool
    :return: Dict of classrooms from database --> dict{classroom_id: common.Classroom
    """
    client_socket.send(encrypt_message(Enum.GET_CLASSROOMS))
    file_size = decrypt_message(client_socket.recv(4096))
    if file_size == 'no classrooms found':
        messagebox.showerror("Input Error", "There Are No classrooms In The System")
        return 'no classrooms found'
    else:
        classrooms = json.loads(decrypt_message(client_socket.recv(int(file_size))))  # Convert json string to list[list]
        classrooms_dict = {}
        if original:
            for classroom in classrooms:
                available = [
                     [True, True, True, True, True, True, True, True, True, True, True],
                     [True, True, True, True, True, True, True, True, True, True, True],
                     [True, True, True, True, True, True, True, True, True, True, True],
                     [True, True, True, True, True, True, True, True, True, True, True],
                     [True, True, True, True, True, True, True, True, True, True, True],
                     [True, True, True, True, True, True, True, True, True, True, True]
                ]
                classrooms_dict[classroom[0]] = Classroom(classroom[1], available)
        else:
            for classroom in classrooms:
                classrooms_dict[classroom[0]] = Classroom(classroom[1], classroom[2])
        return classrooms_dict


if __name__ == "__main__":
    windows.LoginWindow()
