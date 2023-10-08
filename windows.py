import tkinter as tk
from objects import Teacher, Grade, Subject
import client

subjects = None
teachers = None


class BaseWindow(tk.Tk):

    def __init__(self, title, width=800, height=800):
        super().__init__()
        self.title(f'{title}')
        self.geometry(f'{width}x{height}')


class BaseChildWindow:
    def __init__(self, parent, title):
        self.parent = parent
        self.window = tk.Toplevel(self.parent)
        self.window.title(f'{title}')
        self.parent.withdraw()


class LoginWindow(BaseWindow):

    def __init__(self):
        super().__init__('Login', 440, 300)

        username_label = tk.Label(self, text="Username:", font=('Helvetica bold', 26))
        username_label.place(x=0, y=0)

        username_entry = tk.Entry(self, borderwidth=10, font=('Helvetica bold', 15))
        username_entry.place(x=200, y=5)

        password_label = tk.Label(self, text="Password:", font=('Helvetica bold', 26))
        password_label.place(x=0, y=70)

        password_entry = tk.Entry(self, show="*", borderwidth=10, font=('Helvetica bold', 15))  # Hide the password
        password_entry.place(x=200, y=75)

        login_button = tk.Button(self, text="Login", cursor='hand2', borderwidth=10, font=('Helvetica bold', 26), command=lambda: client.check_credentials(self, username_entry, password_entry))
        login_button.place(x=150, y=210)

        self.mainloop()


class AddSubjectWindow(BaseChildWindow):

    def __init__(self, parent):
        super().__init__(parent=parent, title='Add Subject')

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
        global subjects
        super().__init__(parent, 'Add Teacher')

        # Create labels and entry fields
        tk.Label(self.window, text="Enter Teacher Full Name:").pack()
        self.teacher_name_entry = tk.Entry(self.window)
        self.teacher_name_entry.pack()

        tk.Label(self.window, text="Enter Teacher Password:").pack()
        self.teacher_password_entry = tk.Entry(self.window)
        self.teacher_password_entry.pack()

        tk.Label(self.window, text="Choose Teacher Subject:").pack()

        scrollbar = tk.Scrollbar(self.window)
        scrollbar.pack(side='left', fill='y')

        self.teacher_subject_listbox = tk.Listbox(self.window, selectmode='single', yscrollcommand=scrollbar.set)

        if str(type(subjects)) != "<class 'dict'>":
            subjects = client.get_subjects()

        if subjects != 'no subjects found':
            for e, i in enumerate(subjects.values()):
                self.teacher_subject_listbox.insert(e, i.name)
            self.teacher_subject_listbox.pack(side='left', fill='both')
            scrollbar.config(command=self.teacher_subject_listbox.yview)

            tk.Label(self.window, text="Choose Teacher's Day Off:").pack()
            dow_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            var = tk.StringVar(self.window)
            self.teacher_day_off_spinbox = tk.Spinbox(self.window, textvariable=var, value=dow_list, increment=2, width=10, font=('sans-serif', 18),)
            self.teacher_day_off_spinbox.pack()

            tk.Label(self.window, text="Enter Teacher's Max Hours Of Teaching Per Day:").pack()
            self.teacher_max_hours_day_entry = tk.Entry(self.window)
            self.teacher_max_hours_day_entry.pack()

            tk.Label(self.window, text="Enter Teacher's Max Hours Of Teaching Per Friday:").pack()
            self.teacher_max_hours_friday_entry = tk.Entry(self.window)
            self.teacher_max_hours_friday_entry.pack()

            # Create a button to add the teacher
            (tk.Button(self.window, text="Add Teacher",
                      command=lambda: client.add_teacher(
                          self.teacher_name_entry,
                          self.teacher_password_entry,
                          get_selected_item_id(self.teacher_subject_listbox, subjects),
                          dow_list.index(var.get()),
                          self.teacher_max_hours_day_entry,
                          self.teacher_max_hours_friday_entry,
                          self.window,
                          self.parent
                          )).pack())

            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        else:
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.parent.deiconify()  # Show the parent window again
        self.window.destroy()


class AddGradeWindow(BaseChildWindow):
    # TODO: finish ADDGRADEWindow

    def __init__(self, parent):
        super().__init__(parent, 'Add Grade')

        tk.Label(self.window, text="Enter Grade Name:").pack()
        self.grade_name_entry = tk.Entry(self.window)
        self.grade_name_entry.pack()




class MainApplicationAdmin(BaseWindow):
# TODO: finish commented buttons
    def __init__(self):
        super().__init__('SSM - School Schedule Manager')

        # Create buttons to open the "Add Subject" and "Add Teacher" windows
        tk.Button(self, text="Add Subject", command=lambda: AddSubjectWindow(parent=self)).pack()
        tk.Button(self, text="Add Teacher", command=lambda: AddTeacherWindow(parent=self)).pack()
# tk.Button(self, text="Add Grade", command=lambda: AddGradeWindow(self)).pack()

        # Create a buttons to open the "view all teachers" and "view all subjects" windows
        tk.Button(self, text="View All Teachers", command=self.view_all_teachers).pack()
        tk.Button(self, text="View All Subjects", command=self.view_all_subjects).pack()

    def view_all_teachers(self):
        global teachers
        # Create a new window to display the list of teachers
        view_window = tk.Toplevel(self)
        view_window.title("All Subjects")

        # Create a text widget to display the list of teachers
        text_widget = tk.Text(view_window, height=10, width=40)
        text_widget.pack()

        if str(type(teachers)) != "<class 'dict'>":
            teachers = client.get_teachers()

        if teachers == 'no teachers found':
            text_widget.insert(tk.END, 'No teachers Found')
        else:
            # Populate the text widget with the list of teachers
            for teacher in teachers.values():
                text_widget.insert(tk.END, f"Teacher Name: {teacher.name}\n")
                text_widget.insert(tk.END, f"Teacher Subject: {teacher.subject}\n")
                text_widget.insert(tk.END, f"Teacher's work hours: {teacher.work_hours}\n\n")

    def view_all_subjects(self):
        global subjects
        # Create a new window to display the list of teachers
        view_window = tk.Toplevel(self)
        view_window.title("All Teachers")

        # Create a text widget to display the list of teachers
        text_widget = tk.Text(view_window, height=10, width=40)
        text_widget.pack()
        # Populate the text widget with the list of teachers
        if str(type(subjects)) != "<class 'dict'>":
            subjects = client.get_subjects()

        if subjects == 'no subjects found':
            text_widget.insert(tk.END, 'No Subjects Found')

        else:
            for subject in subjects.values():
                text_widget.insert(tk.END, f"Subject Name: {subject.name}\n")
                text_widget.insert(tk.END, f"Max Hours Of Subject In A Day: {subject.max_hours_in_a_day}\n\n")


def get_selected_item_id(listbox, dicti):
    # dicti is a dict which consists of [item_id: item_name] (example teachers dict: [3: Teacher_object])
    selected_indices = listbox.curselection()
    if selected_indices:
        selected_index = selected_indices[0]
        value = listbox.get(selected_index)
        key = [k for k in dicti if dicti[k].name == value][0]
        return key
