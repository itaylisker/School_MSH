import tkinter as tk
from objects import Teacher, Grade, Subject
import client


class BaseWindow(tk.Tk):

    def __init__(self, title, width=800, height=800):
        super().__init__()
        self.title(f'{title}')
        self.geometry(f'{width}x{height}')


class BaseChildWindow(tk.Toplevel):
    def __init__(self, parent, title):
        self.parent = parent
        self.window = super().__init__(self.parent)
        self.window.title = title
        self.parent.withdraw()


class LoginWindow(BaseWindow):

    def __init__(self):
        super().__init__('Login')

        username_label = tk.Label(self, text="Username:")
        username_label.pack()

        username_entry = tk.Entry(self)
        username_entry.pack()

        password_label = tk.Label(self, text="Password:")
        password_label.pack()

        password_entry = tk.Entry(self, show="*")  # Hide the password
        password_entry.pack()

        login_button = tk.Button(self, text="Login", cursor='hand2', command=lambda: client.check_credentials(self, username_entry, password_entry))
        login_button.pack()

        self.mainloop()


class AddSubjectWindow(BaseChildWindow):

    def __init__(self, parent):
        super().__init__(parent, 'Add Subject')

        # Create labels and entry fields
        tk.Label(self.window, text="Enter Subject Name:").pack()
        self.subject_name_entry = tk.Entry(self.window)
        self.subject_name_entry.pack()

        tk.Label(self.window, text="Enter Max Hours per Day:").pack()
        self.max_hours_entry = tk.Entry(self.window)
        self.max_hours_entry.pack()

        # Create a button to add the subject
        tk.Button(self.window, text="Add Subject", cursor='hand2',
                  command=lambda:
                  client.add_subject(self.subject_name_entry, self.max_hours_entry, self.window, self.parent)).pack()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.parent.deiconify()  # Show the parent window again
        self.window.destroy()


class AddTeacherWindow(BaseChildWindow):

    def __init__(self, parent):
        super().__init__(parent, 'Add Teacher')

        # Create labels and entry fields
        tk.Label(self.window, text="Enter Teacher Name:").pack()
        self.teacher_name_entry = tk.Entry(self.window)
        self.teacher_name_entry.pack()

        tk.Label(self.window, text="Enter Teacher Password:").pack()
        self.teacher_password_entry = tk.Entry(self.window)
        self.teacher_password_entry.pack()

        tk.Label(self.window, text="Enter Teacher Subject:").pack()
        scrollbar = tk.Scrollbar(self.window)
        scrollbar.pack(side='right', fill='y')
        self.teacher_subject_Listbox = tk.Listbox(self.window, selectmode='single', yscrollcommand=scrollbar.set)
        subjects = client.get_subjects()
        if subjects != 'no subjects found':
            subjects_dict = {}
            for e, i in enumerate(subjects):
                self.teacher_subject_Listbox.insert(e, i[1])
                subjects_dict[str(i[0])] = i[1]
            self.teacher_subject_Listbox.pack(side='left', fill='both')
            scrollbar.config(command=self.teacher_subject_Listbox.yview)

            tk.Label(self.window, text="Enter Teacher's Day Off (1-6):").pack()
            dow_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            var = tk.StringVar()
            self.teacher_day_off_spinbox = tk.Spinbox(self.window, textvariable=var, value=dow_list, increment=2, width=10, font=('sans-serif', 18),)
            self.teacher_day_off_spinbox.pack()

            tk.Label(self.window, text="Enter Teacher's Max Hours Of Teaching Per Day").pack()
            self.teacher_max_hours_day_entry = tk.Entry(self.window)
            self.teacher_max_hours_day_entry.pack()

            tk.Label(self.window, text="Enter Teacher's Max Hours Of Teaching Per Friday").pack()
            self.teacher_max_hours_friday_entry = tk.Entry(self.window)
            self.teacher_max_hours_friday_entry.pack()

            # Create a button to add the teacher
            (tk.Button(self.window, text="Add Teacher",
                      command=lambda: client.add_teacher(
                          self.teacher_name_entry,
                          self.teacher_password_entry,
                          self.get_selected_item_id(subjects_dict),
                          dow_list.index(var.get()),
                          self.teacher_max_hours_day_entry,
                          self.teacher_max_hours_friday_entry,
                          self.window,
                          self.parent
                          )).pack())

            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        else:
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_selected_item_id(self, subjects_dict):
        selected_indices = self.teacher_subject_Listbox.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            return subjects_dict.get(self.teacher_subject_Listbox.get(selected_index))

    def on_closing(self):
        self.parent.deiconify()  # Show the parent window again
        self.window.destroy()


class AddGradeWindow(BaseChildWindow):
    global grades_list
    # TODO: finish ADDGRADEWindow

    def __init__(self, parent):
        super().__init__(parent, 'Add Grade')
        tk.Label(self.window, text="Enter Grade Name:").pack()
        self.grade_name_entry = tk.Entry(self.window)
        self.grade_name_entry.pack()


class MainApplicationAdmin(BaseWindow):
    global teachers_list
    global subjects_list
# TODO: finish commented buttons

    def __init__(self):
        super().__init__('SSM - School Schedule Manager')

        # Create buttons to open the "Add Subject" and "Add Teacher" windows
        tk.Button(self, text="Add Subject", command=lambda: AddSubjectWindow(self)).pack()
        tk.Button(self, text="Add Teacher", command=lambda: AddTeacherWindow(self)).pack()
# tk.Button(self, text="Add Grade", command=lambda: AddGradeWindow(self)).pack()

        # Create a buttons to open the "view all teachers" and "view all subjects" windows
# tk.Button(self, text="View All Teachers", command=self.view_all_teachers).pack()
# tk.Button(self, text="View All Subjects", command=self.view_all_subjects).pack()

    def view_all_teachers(self):
        # Create a new window to display the list of teachers
        view_window = tk.Toplevel(self)
        view_window.title("All Subjects")

        # Create a text widget to display the list of teachers
        text_widget = tk.Text(view_window, height=10, width=40)
        text_widget.pack()

        # Populate the text widget with the list of teachers
        for teacher in teachers_list:
            text_widget.insert(tk.END, f"Teacher Name: {teacher.name}\n")
            text_widget.insert(tk.END, f"Teacher Subject: {teacher.subject.name}\n")
            text_widget.insert(tk.END, f"Teacher's Day Off: {teacher.work_hours.index([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])+1}\n\n")

    def view_all_subjects(self):
        # Create a new window to display the list of teachers
        view_window = tk.Toplevel(self)
        view_window.title("All Teachers")

        # Create a text widget to display the list of teachers
        text_widget = tk.Text(view_window, height=10, width=40)
        text_widget.pack()
        # Populate the text widget with the list of teachers
        for subject in subjects_list:
            text_widget.insert(tk.END, f"Subject Name: {subject.name}\n")
            text_widget.insert(tk.END, f"Max Hours Of Subject In A Day: {subject.max_hours_in_a_day}\n\n")
