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
        if self.parent.winfo_viewable():
            self.parent.withdraw()


class BaseFrame(tk.Frame):
    def __init__(self, master, width=500, height=500, **kwargs):
        super().__init__(master, **kwargs)
        self.config(f'{width}x{height}')
        self.pack()


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

        self.protocol("WN_DELETE_WINDOW", lambda: client.close_connection(self))
        self.mainloop()


class AddSubjectFrame(tk.Frame):

    def __init__(self, parent):
        def previous_window():
            self.destroy()
            parent.create_main_app_frame()

        global subjects
        parent.winfo_children()[0].destroy()
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


class AddTeacherFrame(tk.Frame):

    def __init__(self, parent):
        def previous_window():
            self.destroy()
            parent.create_main_app_frame()

        global subjects
        global teachers

        parent.winfo_children()[0].destroy()
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


class AddGradeFrame(tk.Frame):
    def __init__(self, parent):
        def previous_window():
            self.destroy()
            parent.create_main_app_frame()

        global subjects
        self.parent = parent

        parent.winfo_children()[0].destroy()
        super().__init__(parent)
        self.pack()

        tk.Button(self, text="Back", command=previous_window).pack()

        tk.Label(self, text="Enter grade name:").pack()
        self.grade_name_entry = tk.Entry(self)
        self.grade_name_entry.pack()

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
            client.add_grade(self.grade_name_entry, hours_per_subject, subject_hours_window, self)

            # go back to main window
            close()
            self.destroy()
            self.parent.create_main_app_frame()

        if self.grade_name_entry.get().strip() =='':
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


class MainApplicationAdmin(BaseWindow):
    # TODO: finish commented buttons
    def __init__(self):
        super().__init__('SSM - School Schedule Manager')
        self.create_main_app_frame()

    def create_main_app_frame(self):
        main_app_frame = tk.Frame(self)
        main_app_frame.pack()
        # Create buttons to open the "Add Subject" and "Add Teacher" windows
        tk.Button(main_app_frame, text="Add Subject", command=lambda: AddSubjectFrame(parent=self)).pack()
        tk.Button(main_app_frame, text="Add Teacher", command=lambda: AddTeacherFrame(parent=self)).pack()
        tk.Button(main_app_frame, text="Add Grade", command=lambda: AddGradeFrame(self)).pack()

        # Create a buttons to open the "view all teachers" and "view all subjects" windows
        tk.Button(main_app_frame, text="View All Teachers", command=self.view_all_teachers).pack()
        tk.Button(main_app_frame, text="View All Subjects", command=self.view_all_subjects).pack()
        self.protocol("WM_DELETE_WINDOW", lambda: client.close_connection(self))

    def view_all_teachers(self):
        global teachers
        # Create a new window to display the list of teachers
        view_window = tk.Toplevel(self)
        view_window.title("All teachers")

        # Create a text widget to display the list of teachers
        text_widget = tk.Text(view_window, height=10, width=40)
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
                text_widget.insert(tk.END, f"Teacher Subject: {teacher.subject}\n")
                text_widget.insert(tk.END, f"Teacher's work hours: {teacher.work_hours}\n\n")

    def view_all_subjects(self):
        global subjects
        # Create a new window to display the list of teachers
        view_window = tk.Toplevel(self)
        view_window.title("All subjects")

        # Create a text widget to display the list of teachers
        text_widget = tk.Text(view_window, height=10, width=40)
        text_widget.pack()
        # Populate the text widget with the list of teachers
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
