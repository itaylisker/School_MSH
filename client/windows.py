import tkinter as tk
import client
from tkHyperlinkManager import HyperlinkManager
import webbrowser
from functools import partial
subjects = None
teachers = None
grades = None
classrooms = None


class BaseWindow(tk.Tk):

    def __init__(self, title, width=800, height=800):
        super().__init__()
        self.title(f'{title}')
        self.geometry(f'{width}x{height}')
        self.config(bg="#E0F2F1")


class BaseChildWindow:
    def __init__(self, parent, title):
        self.parent = parent
        self.window = tk.Toplevel(self.parent)
        self.window.title(f'{title}')
        if self.parent.winfo_viewable():
            self.parent.withdraw()


class BaseFrame(tk.Frame):
    def __init__(self, master, width=500, height=500, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)
        self.config(bg='#E0F2F1')
        self.pack()


class LoginWindow(BaseWindow):
    def __init__(self):
        super().__init__("Login", 440, 300)

        # Create labels and entry fields
        username_label = tk.Label(self, text="Username:", font=("Arial", 16), fg="blue")
        username_label.place(x=20, y=20)

        username_entry = tk.Entry(self, borderwidth=2, font=("Arial", 14))
        username_entry.place(x=150, y=20)

        password_label = tk.Label(self, text="Password:", font=("Arial", 16), fg="blue")
        password_label.place(x=20, y=70)

        password_entry = tk.Entry(self, show="*", borderwidth=2, font=("Arial", 14))
        password_entry.place(x=150, y=70)

        # Create login button
        login_button = tk.Button(self, text="Login", cursor="hand2", font=("Arial", 16), bg="green", fg="white", command=lambda: client.check_credentials(self, username_entry, password_entry))
        login_button.place(x=180, y=150)

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", lambda: client.close_connection(self))
        self.mainloop()


class AddSubjectFrame(BaseFrame):

    def __init__(self, parent):
        def previous_window():
            self.destroy()
            parent.create_main_app_frame()

        global subjects
        parent.add_data_frame.destroy()
        super().__init__(parent)
        self.pack()

        tk.Button(self, text="Back", command=previous_window).pack()
        # Create labels and entry fields
        tk.Label(self, text="Enter Subject Name:").pack()
        self.subject_name_entry = tk.Entry(self)
        self.subject_name_entry.pack()

        tk.Label(self, text="Enter Max Hours per Day:").pack()
        self.max_hours_entry = tk.Entry(self)
        self.max_hours_entry.pack()

        # Create a button to add the subject
        (tk.Button(self, text="Add Subject", cursor='hand2',
                   command=lambda:
                   client.add_subject(self.subject_name_entry, self.max_hours_entry, self, parent, subjects)).pack())


class AddTeacherFrame(BaseFrame):

    def __init__(self, parent):
        def previous_window():
            self.destroy()
            parent.create_main_app_frame()

        global subjects
        global teachers

        parent.add_data_frame.destroy()
        super().__init__(parent)
        self.pack()

        tk.Button(self, text="Back", command=previous_window).pack()
        # Create labels and entry fields
        tk.Label(self, text="Enter Teacher Full Name:").pack()
        self.teacher_name_entry = tk.Entry(self)
        self.teacher_name_entry.pack()

        tk.Label(self, text="Enter Teacher Password:").pack()
        self.teacher_password_entry = tk.Entry(self)
        self.teacher_password_entry.pack()

        tk.Label(self, text="Choose Teacher Subject:").pack()

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side='left', fill='y')

        self.teacher_subject_listbox = tk.Listbox(self, selectmode='single', yscrollcommand=scrollbar.set)

        if type(subjects) != dict:
            subjects = client.get_subjects()

        if subjects == 'no subjects found':
            previous_window()
        else:
            for e, i in enumerate(subjects.values()):
                self.teacher_subject_listbox.insert(e, i.name)
            self.teacher_subject_listbox.pack(side='left', fill='both')
            scrollbar.config(command=self.teacher_subject_listbox.yview)

            tk.Label(self, text="Choose Teacher's Day Off:").pack()
            dow_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            var = tk.StringVar(self)
            self.teacher_day_off_spinbox = tk.Spinbox(self, textvariable=var, value=dow_list, increment=2, width=10, font=('sans-serif', 18), state='readonly')
            self.teacher_day_off_spinbox.pack()

            tk.Label(self, text="Enter Teacher's Max Hours Of Teaching Per Day:").pack()
            self.teacher_max_hours_day_entry = tk.Entry(self)
            self.teacher_max_hours_day_entry.pack()

            tk.Label(self, text="Enter Teacher's Max Hours Of Teaching Per Friday:").pack()
            self.teacher_max_hours_friday_entry = tk.Entry(self)
            self.teacher_max_hours_friday_entry.pack()

            # Create a button to add the teacher
            (tk.Button(self, text="Add Teacher",
                       command=lambda: client.add_teacher(
                          self.teacher_name_entry,
                          self.teacher_password_entry,
                          get_selected_item_id(self.teacher_subject_listbox, subjects),
                          dow_list.index(var.get()),
                          self.teacher_max_hours_day_entry,
                          self.teacher_max_hours_friday_entry,
                          self,
                          parent,
                          teachers,
                          subjects
                          )).pack())


class AddGradeFrame(BaseFrame):
    def __init__(self, parent):
        def previous_window():
            self.destroy()
            parent.create_main_app_frame()

        global subjects
        self.parent = parent

        parent.add_data_frame.destroy()
        super().__init__(parent)
        self.pack()

        tk.Button(self, text="Back", command=previous_window).pack()

        tk.Label(self, text="Enter grade name:").pack()
        self.grade_name_entry = tk.Entry(self)
        self.grade_name_entry.pack()

        tk.Label(self, text="Enter grade's maximum hours per day:").pack()
        self.grade_max_hours_per_day_entry = tk.Entry(self)
        self.grade_max_hours_per_day_entry.pack()

        tk.Label(self, text="Enter grade's maximum hours per friday:").pack()
        self.grade_max_hours_per_friday_entry = tk.Entry(self)
        self.grade_max_hours_per_friday_entry.pack()

        tk.Label(self, text="Choose subjects that the class will study:").pack()

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side='left', fill='y')

        self.subjects_listbox = tk.Listbox(self, selectmode='multiple', yscrollcommand=scrollbar.set)

        if type(subjects) != dict:
            subjects = client.get_subjects()

        if subjects == 'no subjects found':
            previous_window()
        else:
            for e, i in enumerate(subjects.values()):
                self.subjects_listbox.insert(e, i.name)
            self.subjects_listbox.pack(side='left', fill='both')
            scrollbar.config(command=self.subjects_listbox.yview)

            tk.Button(self, text='Finish choosing subjects', command=lambda: self.hours_per_grade(get_selected_items_as_shown_to_user(self.subjects_listbox))).pack()

    def hours_per_grade(self, selected_subjects):
        def close():
            subject_hours_window.destroy()
            self.parent.deiconify()

        def submit(hours_per_subject_dict, spin_list):
            for index, subject in enumerate(hours_per_subject_dict.keys()):
                hours_per_subject_dict[subject] = spin_list[index].get()

            print(hours_per_subject)
            client.add_grade(self.grade_name_entry, self.grade_max_hours_per_day_entry, self.grade_max_hours_per_friday_entry, hours_per_subject, subject_hours_window, self, grades, classrooms)

            # go back to main window
            close()
            self.destroy()
            self.parent.create_main_app_frame()

        if self.grade_name_entry.get().strip() == '':
            from tkinter import messagebox
            messagebox.showerror('Input error', 'Grade name can\'t be empty')
            return

        hours_per_subject = {}
        spinbox_list = []
        subject_hours_window = tk.Toplevel(self.parent)

        self.parent.withdraw()
        tk.Label(subject_hours_window,
                 text=f'Enter amount of hours {self.grade_name_entry.get()} will study each subject every week').pack()
        for i in selected_subjects:
            tk.Label(subject_hours_window, text=f'{i}').pack()
            hours_per_subject_spinbox = tk.Spinbox(subject_hours_window, from_=1, to=10, state='readonly')
            hours_per_subject_spinbox.pack()
            spinbox_list.append(hours_per_subject_spinbox)
            hours_per_subject[i] = 1
        tk.Button(subject_hours_window, text='submit', command=lambda: submit(hours_per_subject, spinbox_list)).pack()
        subject_hours_window.protocol("WM_DELETE_WINDOW", close)


class DeleteSubjectFrame(BaseFrame):
    def __init__(self, parent):
        def previous_window():
            self.destroy()
            parent.create_main_app_frame()

        global subjects
        global teachers
        self.parent = parent

        parent.delete_data_frame.destroy()
        super().__init__(parent)
        self.pack()

        tk.Button(self, text="Back", command=previous_window).pack(padx=250)

        if type(subjects) != dict:
            subjects = client.get_subjects()
        if type(teachers) != dict:
            teachers = client.get_teachers()

        if subjects == 'no subjects found':
            previous_window()

        elif teachers == 'no teachers found':

            canvas = tk.Canvas(self)
            scrollbar = tk.Scrollbar(self, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)

            for i, subject in enumerate(subjects.values()):

                subject_frame = tk.Frame(scrollable_frame, bd=1, relief=tk.SOLID)
                subject_frame.pack(fill='x', padx=10, pady=5)

                tk.Label(subject_frame, text=f"Subject Name: {subject.name}", wraplength=300, anchor='w',
                         justify='left').pack(fill='x')
                tk.Label(subject_frame, text=f"Max Hours Of Subject In A Day: {subject.max_hours_in_a_day}",
                         wraplength=300, anchor='w', justify='left').pack(fill='x')

                if i != len(subjects) - 1:
                    tk.Frame(scrollable_frame, height=1, bg="black").pack(fill='x', padx=10, pady=5)

            scrollbar.pack(side='right', fill='y')
            canvas.pack(side='left', fill='both', expand=True)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        else:

            canvas = tk.Canvas(self)
            scrollbar = tk.Scrollbar(self, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)

            for i, (subject_id, subject) in enumerate(subjects.items()):

                teachers_of_subject = [teacher.name for teacher in teachers.values() if teacher.subject == subject.name]

                subject_frame = tk.Frame(scrollable_frame, bd=1, relief=tk.SOLID)
                subject_frame.pack(fill='x', padx=10, pady=5)

                tk.Label(subject_frame, text=f"Subject Name: {subject.name}", wraplength=300, anchor='w',
                         justify='left').pack(fill='x')
                tk.Label(subject_frame, text=f"Max Hours Of Subject In A Day: {subject.max_hours_in_a_day}",
                         wraplength=300, anchor='w', justify='left').pack(fill='x')

                if teachers_of_subject:

                    tk.Label(subject_frame, text=f'{subject.name} teachers: {", ".join(teachers_of_subject)}',
                             wraplength=300, anchor='w', justify='left').pack(fill='x')

                else:

                    tk.Button(subject_frame, text='DELETE',
                              command=lambda sid=subject_id, sname=subject.name: self.delete_subject(sid, sname)).pack(fill='x')

                if i != len(subjects) - 1:
                    tk.Frame(scrollable_frame, height=1, bg="black").pack(fill='x', padx=10, pady=5)

            scrollbar.pack(side='right', fill='y')
            canvas.pack(side='left', fill='both', expand=True)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def delete_subject(self, subject_id, subject_name):
        global grades
        if type(grades) != dict:
            grades = client.get_grades()
        if grades == 'no grades found':
            client.delete_subject(subject_id, subject_name, self, self.parent, grades, subjects)
        else:
            grades_studying_subject = [grade_id for grade_id, grade in grades.items() if subject_name in grade.hours_per_subject.keys()]
            print(grades_studying_subject)
            client.delete_subject(subject_id, subject_name, self, self.parent, grades, subjects, grades_studying_subject)


class DeleteTeacherFrame(BaseFrame):
    def __init__(self, parent):
        def previous_window():
            self.destroy()
            parent.create_main_app_frame()

        global teachers
        self.parent = parent

        parent.delete_data_frame.destroy()
        super().__init__(parent)
        self.pack()

        tk.Button(self, text="Back", command=previous_window).pack()

        if type(teachers) != dict:
            teachers = client.get_teachers()

        if teachers == 'no teachers found':
            previous_window()

        else:

            canvas = tk.Canvas(self)
            scrollbar = tk.Scrollbar(self, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)

            for i, (teacher_id, teacher) in enumerate(teachers.items()):

                teacher_frame = tk.Frame(scrollable_frame, bd=1, relief=tk.SOLID)
                teacher_frame.pack(fill='x', padx=10, pady=5)

                tk.Label(teacher_frame, text=f"Teacher Name: {teacher.name}", wraplength=300, anchor='w',
                         justify='left').pack(fill='x')
                tk.Label(teacher_frame, text=f"Teacher Subject: {teacher.subject}",
                         wraplength=300, anchor='w', justify='left').pack(fill='x')

                tk.Button(teacher_frame, text=f'DELETE',
                          command=lambda tid=teacher_id, tname=teacher.name: self.delete_teacher(tid, tname)).pack(fill='x')

                if i != len(teachers) - 1:
                    tk.Frame(scrollable_frame, height=1, bg="black").pack(fill='x', padx=10, pady=5)

            scrollbar.pack(side='right', fill='y')
            canvas.pack(side='left', fill='both', expand=True)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def delete_teacher(self, teacher_id, teacher_name):
        client.delete_teacher(teacher_id, teacher_name, self, self.parent, teachers)


class DeleteGradeFrame(BaseFrame):
    def __init__(self, parent):
        def previous_window():
            self.destroy()
            parent.create_main_app_frame()

        global grades
        self.parent = parent

        parent.delete_data_frame.destroy()
        super().__init__(parent)
        self.pack()

        tk.Button(self, text="Back", command=previous_window).pack()

        if type(grades) != dict:
            grades = client.get_grades()

        if grades == 'no grades found':
            previous_window()

        else:

            canvas = tk.Canvas(self)
            scrollbar = tk.Scrollbar(self, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)

            for i, (grade_id, grade) in enumerate(grades.items()):

                grade_frame = tk.Frame(scrollable_frame, bd=1, relief=tk.SOLID)
                grade_frame.pack(fill='x', padx=10, pady=5)

                tk.Label(grade_frame, text=f"Grade Name: {grade.name}", wraplength=300, anchor='w',
                         justify='left').pack(fill='x')
                tk.Label(grade_frame, text=f"Grade Hours Per Subject: {grade.hours_per_subject}",
                         wraplength=300, anchor='w', justify='left').pack(fill='x')

                tk.Button(grade_frame, text='DELETE',
                          command=lambda gid=grade_id, gname=grade.name: self.delete_grade(gid, gname)).pack(fill='x')

                if i != len(grades) - 1:
                    tk.Frame(scrollable_frame, height=1, bg="black").pack(fill='x', padx=10, pady=5)

            scrollbar.pack(side='right', fill='y')
            canvas.pack(side='left', fill='both', expand=True)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def delete_grade(self, grade_id, grade_name):
        global classrooms
        if type(classrooms) != dict:
            classrooms = client.get_classrooms()
        classroom_id = [classroom_id for classroom_id, classroom in classrooms.items() if classroom.name == grade_name][0]
        print(classroom_id)
        client.delete_grade(grade_id, grade_name, classroom_id, self, self.parent, grades, classrooms)


class MainApplication(BaseWindow):
    def __init__(self):
        super().__init__("SSM - School Schedule Manager")
        self.create_main_app_frame()
        self.protocol("WM_DELETE_WINDOW", lambda: client.close_connection(self))

    def create_main_app_frame(self):
        # Color scheme: Teal and Orange
        bg_color = "#E0F2F1"  # Teal background
        button_bg_color = "#FF9800"  # Orange buttons
        button_fg_color = "white"  # White text

        self.main_app_frame = tk.Frame(self)
        self.main_app_frame.config(bg=bg_color)
        self.main_app_frame.pack(padx=20, pady=20)

        tk.Label(self.main_app_frame, text="School Schedule Manager", font=("Arial", 18), bg=bg_color).pack(fill="x", pady=10)
        tk.Button(self.main_app_frame, text="View data", command=self.view_data, font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.main_app_frame, text="Add data", command=self.add_data, font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.main_app_frame, text="Delete data", command=self.delete_data, font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)

    def back_to_home(self, fromm):
        if fromm == 'view':
            self.view_data_frame.destroy()
        elif fromm == 'add':
            self.add_data_frame.destroy()
        else:
            self.delete_data_frame.destroy()
        self.create_main_app_frame()

    def view_data(self):
        self.main_app_frame.destroy()
        # Color scheme: Teal and Orange
        bg_color = "#E0F2F1"  # Teal background
        button_bg_color = "#FF9800"  # Orange buttons
        button_fg_color = "white"  # White text

        self.view_data_frame = tk.Frame(self)
        self.view_data_frame.config(bg=bg_color)
        self.view_data_frame.pack(padx=20, pady=20)

        tk.Label(self.view_data_frame, text="View Data", bg=bg_color, font=("Arial", 16)).pack(fill="x", pady=10)
        tk.Button(self.view_data_frame, text="View all teachers", command=self.view_all_teachers, font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.view_data_frame, text="View all subjects", command=self.view_all_subjects, font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.view_data_frame, text='View all grades', command=self.view_all_grades, font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.view_data_frame, text='View all classrooms', command=self.view_all_classrooms, font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.view_data_frame, text='Back to home', command=lambda: self.back_to_home('view'), font=("Arial", 14)).pack(fill="x", pady=10)

    def add_data(self):
        self.main_app_frame.destroy()

        # Color scheme: Teal and Orange
        bg_color = "#E0F2F1"  # Teal background
        button_bg_color = "#FF9800"  # Orange buttons
        button_fg_color = "white"  # White text

        self.add_data_frame = tk.Frame(self)
        self.add_data_frame.config(bg=bg_color)
        self.add_data_frame.pack(padx=20, pady=20)

        tk.Label(self.add_data_frame, text="Add Data", bg=bg_color, font=("Arial", 16)).pack(fill="x", pady=10)
        tk.Button(self.add_data_frame, text="Add subject", command=lambda: AddSubjectFrame(parent=self), font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.add_data_frame, text="Add teacher", command=lambda: AddTeacherFrame(parent=self), font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.add_data_frame, text="Add grade", command=lambda: AddGradeFrame(self), font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.add_data_frame, text='Create schedules', command=lambda: client.create_schedules(grades, subjects), font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.add_data_frame, text='Back to home', command=lambda: self.back_to_home('add'), font=("Arial", 14)).pack(fill="x", pady=10)

    def delete_data(self):
        self.main_app_frame.destroy()

        # Color scheme: Teal and Orange
        bg_color = "#E0F2F1"  # Teal background
        button_bg_color = "#FF9800"  # Orange buttons
        button_fg_color = "white"  # White text

        self.delete_data_frame = tk.Frame(self)
        self.delete_data_frame.config(bg=bg_color)
        self.delete_data_frame.pack(padx=20, pady=20)

        tk.Button(self.delete_data_frame, text="Delete subject", command=lambda: DeleteSubjectFrame(parent=self),
                  font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.delete_data_frame, text="Delete teacher", command=lambda: DeleteTeacherFrame(parent=self),
                  font=("Arial", 14), bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.delete_data_frame, text="Delete grade", command=lambda: DeleteGradeFrame(self), font=("Arial", 14),
                  bg=button_bg_color, fg=button_fg_color).pack(fill="x", pady=10)
        tk.Button(self.delete_data_frame, text='Back to home', command=lambda: self.back_to_home('delete'),
                  font=("Arial", 14)).pack(fill="x", pady=10)

    def view_all_teachers(self):
        global teachers

        # Create a new window to display the list of teachers
        view_window = tk.Toplevel(self)
        view_window.title("All teachers")
        view_window.config(padx=100, pady=100)

        # Create a text widget to display the list of teachers
        text_widget = tk.Text(view_window, height=100, width=100)
        text_widget.pack()
        if teachers:
            print(f'type: {type(teachers)}, teachers: {[i.name for i in teachers.values()]}')

        if type(teachers) != dict:
            teachers = client.get_teachers()

        if teachers == 'no teachers found':
            text_widget.insert(tk.END, 'No teachers Found')
        else:
            # Populate the text widget with the list of teachers
            for teacher in teachers.values():
                text_widget.insert(tk.END, f"Teacher Name: {teacher.name}\n")
                text_widget.insert(tk.END, f"Teacher Subject: {teacher.subject}\n\n")

    def view_all_subjects(self):
        global subjects
        # Create a new window to display the list of subjects
        view_window = tk.Toplevel(self)
        view_window.title("All subjects")
        view_window.config(pady=100, padx=100)

        # Create a text widget to display the list of subjects
        text_widget = tk.Text(view_window, height=100, width=100)
        text_widget.pack()
        # Populate the text widget with the list of subjects
        if subjects:
            print(f'type: {type(subjects)}, subjects: {[i.name for i in subjects.values()]}')
        if type(subjects) != dict:
            subjects = client.get_subjects()

        if subjects == 'no subjects found':
            text_widget.insert(tk.END, 'No Subjects Found')

        else:
            for subject in subjects.values():
                text_widget.insert(tk.END, f"Subject Name: {subject.name}\n")
                text_widget.insert(tk.END, f"Max Hours Of Subject In A Day: {subject.max_hours_in_a_day}\n\n")

    def view_all_grades(self):
        global grades
        # Create a new window to display the list of grades

        def callback(url):
            webbrowser.open_new_tab(url)

        view_window = tk.Toplevel(self)
        view_window.title("All grades")
        view_window.config(pady=100, padx=100)

        # Create a text widget to display the list of grades
        text_widget = tk.Text(view_window, height=100, width=100)
        text_widget.pack()

        if type(grades) != dict:
            grades = client.get_grades()

        if grades == 'no grades found':
            text_widget.insert(tk.END, 'No grades Found')
        else:
            hyperlink = HyperlinkManager(text_widget)

            for grade in grades.values():
                text_widget.insert(tk.END, f'Grade name: {grade.name}\n')
                text_widget.insert(tk.END, f'Grade\'s hours per subject: {grade.hours_per_subject}\n')
                print(grade.name)
                text_widget.insert(tk.END, f"{grade.name}'s schedule\n\n", hyperlink.add(partial(webbrowser.open, f"http://127.0.0.1/class/{grade.name}")))

    def view_all_classrooms(self):
        global classrooms
        # Create a new window to display the list of grades
        view_window = tk.Toplevel(self)
        view_window.title("All classrooms")
        view_window.config(pady=100, padx=100)

        # Create a text widget to display the list of grades
        text_widget = tk.Text(view_window, height=100, width=100)
        text_widget.pack()

        if type(classrooms) != dict:
            classrooms = client.get_classrooms()

        if classrooms == 'no classrooms found':
            text_widget.insert(tk.END, 'No classrooms Found')

        else:
            for classroom in classrooms.values():
                text_widget.insert(tk.END, f'Classroom name: {classroom.name}\n')


def get_selected_item_id(listbox, dicti):
    # dicti is a dict which consists of [item_id: item] (example teachers dict: [3: Teacher_object]) 
    selected_indices = listbox.curselection()
    if selected_indices:
        selected_index = selected_indices[0]
        value = listbox.get(selected_index)
        key = [k for k in dicti if dicti[k].name == value][0]
        return key


def get_selected_items_as_shown_to_user(listbox):
    selected_indices = list(listbox.curselection())
    selected_values = [listbox.get(index) for index in selected_indices]
    return selected_values
