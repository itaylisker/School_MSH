import tkinter as tk
from tkinter import messagebox
import teacher, grade, subject

hours_per_subject = {}
subjects_list = []
teachers_list = []
grades_list = []
DOW_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


class AddSubjectWindow:
    global subjects_list

    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Add Subject")
        self.parent.withdraw()  # Hide the parent window while this window is open

        # Create labels and entry fields
        tk.Label(self.window, text="Enter Subject Name:").pack()
        self.subject_name_entry = tk.Entry(self.window)
        self.subject_name_entry.pack()

        tk.Label(self.window, text="Enter Max Hours per Day:").pack()
        self.max_hours_entry = tk.Entry(self.window)
        self.max_hours_entry.pack()

        # Create a button to add the subject
        tk.Button(self.window, text="Add Subject", command=self.add_subject).pack()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_subject(self):
        subject_name = self.subject_name_entry.get()
        max_hours = self.max_hours_entry.get()

        if not subject_name or not max_hours:
            messagebox.showerror("Input Error", "Both fields must be filled.")
        elif subject_name.lower() in [i.name for i in subjects_list]:
            messagebox.showerror("Input Error", "Subject Already Exists.")
        else:
            new_sub = subject.Subject(subject_name.lower(), int(max_hours))
            subjects_list.append(new_sub)
            print(f"Subject Name: {subject_name}, Max Hours per Day: {max_hours}")
            self.window.destroy()  # Close the window
            self.parent.deiconify()  # Show the parent window again

    def on_closing(self):
        self.parent.deiconify()  # Show the parent window again
        self.window.destroy()


class AddTeacherWindow:
    global teachers_list

    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Add Teacher")
        self.parent.withdraw()  # Hide the parent window while this window is open

        # Create labels and entry fields
        tk.Label(self.window, text="Enter Teacher Name:").pack()
        self.teacher_name_entry = tk.Entry(self.window)
        self.teacher_name_entry.pack()

        tk.Label(self.window, text="Enter Teacher Subject:").pack()
        self.teacher_subject_entry = tk.Entry(self.window)
        self.teacher_subject_entry.pack()

        tk.Label(self.window, text="Enter Teacher's Day Off (1-6):").pack()
        self.teacher_day_off_entry = tk.Entry(self.window)
        self.teacher_day_off_entry.pack()

        # Create a button to add the teacher
        tk.Button(self.window, text="Add Teacher", command=self.add_teacher).pack()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_teacher(self):
        teacher_name = self.teacher_name_entry.get()
        teacher_subject = self.teacher_subject_entry.get()
        teacher_day_off = self.teacher_day_off_entry.get()

        if not teacher_name or not teacher_subject or not teacher_day_off:
            messagebox.showerror("Input Error", "All fields must be filled.")
        elif not teacher_day_off.isdigit() or int(teacher_day_off) < 1 or int(teacher_day_off) > 6:
            messagebox.showerror("Input Error", "Teacher's day off must be a number between 1 and 6.")
        elif teacher_subject.lower() not in [i.name for i in subjects_list]:
            messagebox.showerror("Input Error", "Subject does not exist, please add it using the add subject button first.")
        elif teacher_name.lower() in [i.name for i in teachers_list]:
            messagebox.showerror("Input Error", "Teacher already exists.")
        else:
            new_t = teacher.Teacher(teacher_name.lower(), [i for i in subjects_list if i.name == teacher_subject.lower()][0])
            new_t.cant_work(int(teacher_day_off), 0, 1)
            teachers_list.append(new_t)
            print(f"Teacher Name: {teacher_name}, Subject: {teacher_subject}, Day Off: {teacher_day_off}")
            self.window.destroy()  # Close the window
            self.parent.deiconify()  # Show the parent window again

    def on_closing(self):
        self.parent.deiconify()  # Show the parent window again
        self.window.destroy()


class AddGradeWindow:
    global grades_list

    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Add Grade")
        self.parent.withdraw()  # Hide the parent window while this window is open

        tk.Label(self.window, text="Enter Grade Name:").pack()
        self.grade_name_entry = tk.Entry(self.window)
        self.grade_name_entry.pack()


class MainApplication:
    global teachers_list
    global subjects_list

    def __init__(self, root):
        self.root = root
        self.root.title("High School Schedule Organizer")

        # Create buttons to open the "Add Subject" and "Add Teacher" windows
        tk.Button(self.root, text="Add Subject", command=self.open_add_subject_window).pack()
        tk.Button(self.root, text="Add Teacher", command=self.open_add_teacher_window).pack()
        tk.Button(self.root, text="Add Grade", command=self.open_add_grade_window).pack()

        # Create a buttons to open the "view all teachers" and "view all subjects" windows
        tk.Button(self.root, text="View All Teachers", command=self.view_all_teachers).pack()
        tk.Button(self.root, text="View All Subjects", command=self.view_all_subjects).pack()

    def open_add_subject_window(self):
        AddSubjectWindow(self.root)

    def open_add_teacher_window(self):
        AddTeacherWindow(self.root)

    def open_add_grade_window(self):
        AddGradeWindow(self.root)

    def view_all_teachers(self):
        # Create a new window to display the list of teachers
        view_window = tk.Toplevel(self.root)
        view_window.title("All Subjects")

        # Create a text widget to display the list of teachers
        text_widget = tk.Text(view_window, height=10, width=40)
        text_widget.pack()

        # Populate the text widget with the list of teachers
        for teacher in teachers_list:
            text_widget.insert(tk.END, f"Teacher Name: {teacher.name}\n")
            text_widget.insert(tk.END, f"Teacher Subject: {teacher.subject}\n")
            text_widget.insert(tk.END, f"Teacher's Day Off: {teacher.work_hours.index([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])+1}\n\n")

    def view_all_subjects(self):
        # Create a new window to display the list of teachers
        view_window = tk.Toplevel(self.root)
        view_window.title("All Teachers")

        # Create a text widget to display the list of teachers
        text_widget = tk.Text(view_window, height=10, width=40)
        text_widget.pack()
        # Populate the text widget with the list of teachers
        for subject in subjects_list:
            text_widget.insert(tk.END, f"Subject Name: {subject.name}\n")
            text_widget.insert(tk.END, f"Max Hours Of Subject In A Day: {subject.max_hours_in_a_day}\n\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
