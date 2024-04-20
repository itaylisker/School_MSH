from tkinter import messagebox
from common import Teacher, Grade, Subject, Classroom, Lesson
from common import Enum
import windows
import socket
import json

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5050))


def close_connection(window):
    window.destroy()
    client_socket.close()


# Function to check login credentials
def check_credentials(window, username_entry, password_entry):

    username = username_entry.get()
    password = password_entry.get()
    credentials = f'{Enum.LOGIN_INFO},{username},{password}'

    client_socket.send(credentials.encode())
    cred_check = client_socket.recv(1024).decode()

    if cred_check == 'admin':
        windows.MainApplicationAdmin()
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


def create_schedules(teachers, grades, classrooms, subjects):

    if not teachers:
        teachers = get_teachers()
    if not grades:
        grades = get_grades()
    if not classrooms:
        classrooms = get_classrooms()
    if not subjects:
        subjects = get_subjects()

    assigned_lessons_dict = {}
    subjects_lacking_in_teachers = []
    teaching_dict = {}
    # create a dictionary that states which teacher is teaching what class {(grade.name, subject): teacher.name}
    for grade in grades.values():
        for subject in grade.hours_per_subject.keys():
            tup_to_add = (grade.name, subject)
            teaching_dict[tup_to_add] = None

    print(f'{teachers}\n{grades}\n{classrooms}\n{subjects}')
    print('$$$$$$$$$$$$$$$$$$$$$',grades[5].name,grades[5].hours_per_subject)
    def check_if_enough_hours(subject):

        hours_of_subject_for_grades = [(grade.name, grade.hours_per_subject[subject],print('##################',grade.name,grade.hours_per_subject)) for grade in grades.values() if subject in grade.hours_per_subject]
        sorted_hours_of_subject_for_grades = sorted(hours_of_subject_for_grades, key=lambda x: x[1])

        sorted_teachers_of_subject = sorted([[teacher.name, sum([sum(day) for day in teacher.work_hours])] for teacher in teachers.values() if teacher.subject == subject], key=lambda x: x[1])
        print('||||||||||||||||||||||||||||||', sorted_teachers_of_subject,'\n',subject)
        for grade_hours in sorted_hours_of_subject_for_grades:

            grade_name = grade_hours[0]
            grade_hours_of_subject = grade_hours[1]
            print('!!!!!!!!!!!!',grade_name, grade_hours_of_subject)
            for index, teacher_hours in enumerate(sorted_teachers_of_subject):

                teacher_name = teacher_hours[0]
                teacher_hours_of_subject = teacher_hours[1]
                print('@@@@@@@@@@@@@@@@@@@@',teacher_name, teacher_hours_of_subject)
                if teacher_hours_of_subject >= grade_hours_of_subject:
                    teaching_dict[(grade_name, subject)] = teacher_name
                    sorted_teachers_of_subject[index][1] -= grade_hours_of_subject
                    grade_hours_of_subject = 0
                    break
            if grade_hours_of_subject != 0:
                subjects_lacking_in_teachers.append((subject, grade_name))
        return subjects_lacking_in_teachers

    for subject in subjects.values():
        print(check_if_enough_hours(subject.name))

        if len(subjects_lacking_in_teachers) > 0:
            messagebox.showerror(
                "not enough staff",
                f"not enough teachers for subjects: {','.join(subjects_lacking_in_teachers)} "
            )

            return
    print(teaching_dict)
    adjusted_teachers = [teacher for teacher in teachers.values()]
    adjusted_grades = [grade for grade in grades.values()]
    adjusted_classrooms = [classroom for classroom in classrooms.values()]
    adjusted_subjects = {subject.name: subject for subject_id, subject in subjects.items()}


    print(f'{adjusted_teachers}\n{adjusted_grades}\n{adjusted_classrooms}\n{adjusted_subjects}')

    missing_periods = []

    def find_available_teacher(grade_name, teachers, subject, day, hour):
        # Find a teacher who teaches the subject, teaches the given class and is available at the given day and hour
        for teacher in teachers:
            if (teacher.subject == subject
                    and
                    (not teaching_dict[(grade_name, subject)]
                     or
                     teaching_dict[(grade_name, subject)] == teacher.name)):

                if len(teacher.work_hours) >= day + 1 and len(teacher.work_hours[day]) >= hour + 1 and teacher.work_hours[day][hour]:
                    return teacher
        missing_periods.append((grade_name, subject, day, hour))
        return None

    def find_available_classroom(classrooms, day, hour):
        # Find a classroom that is available at the given day and hour
        for classroom in classrooms:
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

    while len(assigned_lessons_dict) != len(teaching_dict):
        for day in range(6):
            for grade in adjusted_grades:


    with open('check1.txt', 'w') as f:
        f.write(json.dumps([[[hour.subject if hour else None for hour in day] for day in schedule] for schedule in
                            [grade.schedule for grade in adjusted_grades]]))
    print([[[hour.subject if hour else None for hour in day] for day in schedule] for schedule in
           [grade.schedule for grade in adjusted_grades]])
    print(grades)
    print(adjusted_grades)
    print("missing::::::", missing_periods)
    return grades


def add_subject(subject_name_entry, max_hours_entry, window, parent, subjects):
    #  TODO: insure that max_hours type is int
    subject_name = subject_name_entry.get().title()
    max_hours = max_hours_entry.get()

    if not (subject_name and max_hours):
        messagebox.showerror("Input Error", "Both Fields Must Be Filled.")
    else:
        subject = f'{Enum.ADD_SUBJECT},{subject_name},{max_hours}'
        client_socket.send(subject.encode())
        response = client_socket.recv(1024).decode()
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
    client_socket.send(f'{Enum.GET_SUBJECTS}'.encode())
    file_size = client_socket.recv(1024).decode()
    if file_size == 'no subjects found':
        messagebox.showerror("Input Error", "There Are No Subjects In The System")
        return 'no subjects found'
    else:
        subjects = json.loads(client_socket.recv(int(file_size)).decode())  # Convert json string to list[list]
        subjects_dict = {}
        for subject in subjects:
            subjects_dict[subject[0]] = Subject(subject[1], subject[2])
        return subjects_dict


def add_teacher(
        teacher_name_entry, teacher_password_entry,
        teacher_subject_id, teacher_day_off_number,
        teacher_max_hours_day_entry, teacher_max_hours_friday_entry,
        window, parent, teachers, subjects
                ):
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
        client_socket.send(teacher.encode())
        response = client_socket.recv(1024).decode()
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


def get_teachers():
    client_socket.send(f'{Enum.GET_TEACHERS}'.encode())
    file_size = client_socket.recv(1024).decode()
    if file_size == 'no teachers found':
        messagebox.showerror("Input Error", "There Are No Teachers In The System")
        return 'no teachers found'
    else:
        teachers = json.loads(client_socket.recv(int(file_size)).decode())  # Convert json string to list[list]
        teachers_dict = {}
        for teacher in teachers:

            teachers_dict[teacher[0]] = Teacher(teacher[1], teacher[-1], teacher[4])
        return teachers_dict


def add_grade(grade_name_entry, hours_per_subject_dict, window, parent):
    from os import path
    grade_name = grade_name_entry.get().title()

    with open('client/jsons/hours_per_subject.json', 'w') as f:
        json.dump(hours_per_subject_dict, f)
    file_size = str(path.getsize('client/jsons/hours_per_subject.json'))
    size_text = f'{Enum.ADD_GRADE},{file_size}'
    client_socket.send(size_text.encode())
    with open('client/jsons/hours_per_subject.json', 'r') as f:
        hours_per_subject_str = f.read()

    grade = f'{grade_name}|{hours_per_subject_str}'
    client_socket.send(grade.encode())
    response = client_socket.recv(1024).decode()
    if response == Enum.EXISTS:
        messagebox.showerror("Input error", "Grade with this name already exists.")
        window.destroy()
        parent.deiconify()
    else:
        messagebox.showinfo('Successfully added', 'Grade added successfully')


def get_grades():
    client_socket.send(Enum.GET_GRADES.encode())
    file_size = client_socket.recv(1024).decode()
    if file_size == 'no grades found':
        messagebox.showerror("Input Error", "There Are No Grades In The System")
        return 'no grades found'
    else:
        grades = json.loads(client_socket.recv(int(file_size)).decode())  # Convert json string to list[list]
        grades_dict = {}
        for grade in grades:
            hours_per_subject = {subject_name.title(): int(hours) for subject_name, hours in grade[2].items()}
            grades_dict[grade[0]] = Grade(grade[1], grade[3], grade[4], hours_per_subject)
        return grades_dict


def add_classroom():
    # TODO: finish func
    pass


def get_classrooms():
    client_socket.send(Enum.GET_CLASSROOMS.encode())
    file_size = client_socket.recv(1024).decode()
    if file_size == 'no classrooms found':
        messagebox.showerror("Input Error", "There Are No classrooms In The System")
        return 'no classrooms found'
    else:
        classrooms = json.loads(client_socket.recv(int(file_size)).decode())  # Convert json string to list[list]
        classrooms_dict = {}
        for classroom in classrooms:
            classrooms_dict[classroom[0]] = Classroom(classroom[1], classroom[2])
        return classrooms_dict


if __name__ == "__main__":
    windows.LoginWindow()
