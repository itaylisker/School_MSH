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

    unassigned_lessons = []
    subjects_lacking_in_teachers = []
    available_hours_per_subject = {
        # dict consists of how many hours are teachable of each subject
        # based on the teachers that are registered in the database and
        # their days off
        subject.name: sum(
            [
                sum(
                    sum(j) for j in i.work_hours
                )
                for i in teachers.values() if i.subject == subject.name
            ]
        )
        for subject in subjects.values()
    }

    print(available_hours_per_subject)
    print(f'{teachers}\n{grades}\n{classrooms}\n{subjects}')

    for grade in grades.values():
        for subject, hours in grade.hours_per_subject.items():
            available_hours_per_subject[subject] -= int(hours)
    for subject, hours in available_hours_per_subject.items():
        if hours < 0:
            subjects_lacking_in_teachers.append(subject)
    if len(subjects_lacking_in_teachers) > 0:
        messagebox.showerror(
            "not enough staff",
            f"not enough teachers for subjects: {','.join(subjects_lacking_in_teachers)} "
        )
        return

    adjusted_teachers = [teacher for teacher in teachers.values()]
    adjusted_grades = [grade for grade in grades.values()]
    adjusted_classrooms = [classroom for classroom in classrooms.values()]
    adjusted_subjects = {subject.name: subject for subject_id, subject in subjects.items()}
    teacher_of_subject_of_each_subject_of_each_class = {}
    # create a dictionary that states which teacher is teaching what class
    for grade in grades.values():
        for subject in grade.hours_per_subject.keys():
            tup_to_add = (grade.name, subject)
            teacher_of_subject_of_each_subject_of_each_class[tup_to_add] = None

    print(f'{adjusted_teachers}\n{adjusted_grades}\n{adjusted_classrooms}\n{adjusted_subjects}')

    missing_periods = []

    def find_available_teacher(grade_name, teachers, subject, day, hour):
        # Find a teacher who teaches the subject and is available at the given day and hour
        for teacher in teachers:
            if (teacher.subject == subject
                    and
                    (not teacher_of_subject_of_each_subject_of_each_class[(grade_name, subject)]
                     or
                     teacher_of_subject_of_each_subject_of_each_class[(grade_name, subject)] == teacher.name)):

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

    def can_schedule(grade, subject, day, hour):
        # Check if the indices are within the valid range
        if day < 0 or day >= len(grade.schedule) or hour < 0 or hour >= len(grade.schedule[day]):
            return False

        # Check if the lesson can be scheduled in this slot
        return grade.schedule[day][hour] is None and \
            sum(1 for lesson in grade.schedule[day] if lesson and lesson.subject == subject) < adjusted_subjects[
                subject].max_hours_in_a_day

    for grade in adjusted_grades:
        for subject, total_hours in sorted(grade.hours_per_subject.items(), key=lambda x: x[1], reverse=True):
            hours_scheduled = 0
            total_hours = int(total_hours)
            while hours_scheduled < total_hours:
                for day in range(6):  # Sunday to Friday
                    for hour in range(8):
                        if hours_scheduled >= total_hours or not can_schedule(grade, subject, day, hour):
                            continue

                        teacher = find_available_teacher(grade.name, adjusted_teachers, subject, day, hour)
                        classroom = find_available_classroom(adjusted_classrooms, day, hour)
                        if teacher and classroom:
                            schedule_lesson(grade, teacher, classroom, day, hour)
                        hours_scheduled += 1

                        if hours_scheduled >= total_hours:
                            break

                    if hours_scheduled >= total_hours:
                        break

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
            grades_dict[grade[0]] = Grade(grade[1], grade[3], grade[4], grade[2])
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
