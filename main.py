import tkinter as tk
import sqlite3
from tkinter import messagebox, ttk
from tkinter import PhotoImage

#--------------------------------------------------------------------------------------------------------

back_btn = None
admin_title_label = None
admin_logout_btn = None
student_logout_btn = None
student_title_label = None
logged_in_roll = None
#--------------------------------------------------------------------------------------------------------

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


#--------------------------------------------------------------------------------------------------------

def show_entry():

    global back_btn, admin_title_label,student_title_label

    clear_frame(center_frame)

    if back_btn:
        back_btn.destroy()
        back_btn = None

    if admin_title_label:
        admin_title_label.destroy()
        admin_title_label = None

    if student_title_label:
        student_title_label.destroy()
        student_title_label = None


    add_logo_and_title()

    tk.Button(center_frame, text="Student", width=15, bg="#0093dd", fg="#ffffff",  
        activebackground="#0078d7", activeforeground="#ffffff", font=("Playfair Display", 14), bd=0, 
        command=show_student).pack(pady=(28,10))

    tk.Button(center_frame, text="Admin", width=15, bg="#333333", fg="#ffffff",  
        activebackground="#0078d7", activeforeground="#ffffff", font=("Playfair Display", 14), bd=0, 
        command=show_admin).pack(pady=10)


#--------------------------------------------------------------------------------------------------------


def add_logo_and_title():
    try:
        logo_img = PhotoImage(file="fast_logo.png") 
        logo = tk.Label(center_frame, image=logo_img, bg="#000000")
        logo.image = logo_img
    except Exception:
        logo = tk.Label(center_frame, text="FAST Logo", font=("Segoe UI", 24, "bold"), bg="#000000", fg="#00ffff")
    logo.pack(pady=10)

    tk.Label(center_frame, text="Timetable Project", font=("Playfair Display", 25, "bold"), bg="#000000", fg="#f1f1f1").pack(pady=13)



#--------------------------------------------------------------------------------------------------------


def show_student():

    global student_title_label, student_logout_btn
    clear_frame(center_frame)

    if student_logout_btn:
        student_logout_btn.destroy()
        student_logout_btn = None 

    if student_title_label:
        student_title_label.destroy()
        student_title_label = None

    add_back_button()

    student_title_label = tk.Label(root, text="Student Panel-Login", font=("Playfair Display", 32, "bold"), bg="#000000", fg="#00ffff")
    student_title_label.place(relx=0.2, y=40, anchor="n")

    form_frame = tk.Frame(center_frame, bg="#0f0f0f", bd=0, relief="groove")  
    form_frame.pack(pady=80, padx=20)

   
    inner_frame = tk.Frame(form_frame, bg="#0f0f0f")
    inner_frame.pack(padx=30, pady=30)

    
    tk.Label(inner_frame, text="Roll-Number:", font=("Playfair Display", 18), bg="#0f0f0f", fg="white")\
        .grid(row=0, column=0, pady=15, padx=10, sticky="w")
    
    username_entry = tk.Entry(inner_frame, font=("Segoe UI", 15), width=25)
    username_entry.grid(row=0, column=1, pady=15, padx=10)


    login_btn = tk.Button(inner_frame, text="Login", font=("Playfair Display", 13, "bold"), bg="#0078d7", fg="white", padx=12, pady=10, bd=0, width=10,command=lambda: student_login(username_entry.get()))
    login_btn.grid(row=2, column=0, columnspan=2, pady=(20, 10))



#--------------------------------------------------------------------------------------------------------


def student_login(roll_number):

    global logged_in_roll
    roll = roll_number.strip()

    if not roll:
        messagebox.showwarning("Input Error", "Please enter your roll number.")
        return

    try:
        conn = sqlite3.connect("timetable.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Students WHERE RollNumber = ?", (roll,))
        result = cursor.fetchone()
        conn.close()

        if result:
            logged_in_roll = roll  # Save it for later use
            students_setting()     # Continue to dashboard
        else:
            messagebox.showerror("Login Failed", "Roll number not found in records.")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")





#--------------------------------------------------------------------------------------------------------

def students_setting():
    
    global student_title_label

    clear_frame(center_frame)

    if student_title_label:
        student_title_label.destroy()
        student_title_label = None

    student_logout_button()


    conn = sqlite3.connect("timetable.db")
    cur = conn.cursor()
    cur.execute("SELECT StudentName FROM Students WHERE RollNumber = ?", (logged_in_roll,))
    result = cur.fetchone()
    conn.close()

    student_name = result[0] if result else "Student"

    student_title_label = tk.Label(root, text=f"Welcome, {student_name}!", font=("Playfair Display", 26, "bold"), bg="#000", fg="#00ffff")
    student_title_label.pack(pady=10)

    # Apply Treeview styling
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Custom.Treeview",
                    background="#333333",
                    foreground="white",
                    fieldbackground="#333333",
                    font=("Segoe UI", 10))
    style.map("Custom.Treeview", background=[("selected", "#0078d7")])

    # ----- Timetable Treeview -----
    timetable_tree = ttk.Treeview(center_frame, columns=("Day", "Time", "Course Code", "Course Name", "Teacher", "Room"),
                                  show='headings', style="Custom.Treeview")
    for col in timetable_tree["columns"]:
        timetable_tree.heading(col, text=col)
        timetable_tree.column(col, anchor="center", width=195)
    timetable_tree.pack(pady=10, fill="both", expand=True)

    # ----- Teacher Info Treeview (initially hidden) -----
    teacher_tree = ttk.Treeview(center_frame, columns=("Name", "Email", "Office Room"),
                                show='headings', style="Custom.Treeview")
    for col in teacher_tree["columns"]:
        teacher_tree.heading(col, text=col)
        teacher_tree.column(col, anchor="center", width=170)

    # ----- Toggle Button -----
    toggle_btn = tk.Button(center_frame, text="View Teacher Info", font=("Playfair Display", 13, "bold"),
                           bg="#0078d7", fg="white")
    toggle_btn.pack(pady=5)

    is_showing_teacher = False  # Track state of view

    # ----- DB Connect Helper -----
    def db_connect():
        try:
            conn = sqlite3.connect("timetable.db")
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")
            return None

    # ----- Load Timetable Immediately -----
    def load_timetable():
        query = """
            SELECT D.DayName,
                   T.StartTime || ' - ' || T.EndTime AS TimeSlot,
                   C.CourseCode,
                   C.CourseName,
                   Te.TeacherName,
                   R.RoomName
            FROM Students S
            JOIN Sections Sec ON S.SectionID = Sec.SectionID
            JOIN CourseOfferings CO ON CO.SectionID = Sec.SectionID
            JOIN Courses C ON CO.CourseID = C.CourseID
            JOIN Teachers Te ON CO.TeacherID = Te.TeacherID
            JOIN ClassTimes CT ON CT.OfferingID = CO.OfferingID
            JOIN Days D ON CT.DayID = D.DayID
            JOIN TimeSlots T ON CT.SlotID = T.SlotID
            JOIN Rooms R ON CT.RoomID = R.RoomID
            WHERE S.RollNumber = ?
            ORDER BY D.DayID, T.SlotID;
        """
        conn = db_connect()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute(query, (logged_in_roll,))
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Query Error", f"Failed to fetch timetable: {e}")
            conn.close()
            return
        conn.close()

        timetable_tree.delete(*timetable_tree.get_children())
        if rows:
            for row in rows:
                timetable_tree.insert("", tk.END, values=row)
        else:
            messagebox.showinfo("No Data", "No timetable found for your roll number.")

    # ----- Toggle View Function -----
    def toggle_view():
        nonlocal is_showing_teacher

        if is_showing_teacher:
            # Switch to timetable
            teacher_tree.pack_forget()
            timetable_tree.pack(pady=10, fill="both", expand=True)
            toggle_btn.config(text="View Teacher Info")
            is_showing_teacher = False
        else:
            # Switch to teacher info
            timetable_tree.pack_forget()
            teacher_tree.delete(*teacher_tree.get_children())

            try:
                conn = sqlite3.connect("timetable.db")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT 
                    Te.TeacherName, 
                    Te.Email, 
                    ORm.RoomName
                    FROM Students S
                    JOIN Sections Sec ON S.SectionID = Sec.SectionID
                    JOIN CourseOfferings CO ON CO.SectionID = Sec.SectionID
                    JOIN Teachers Te ON CO.TeacherID = Te.TeacherID
                    LEFT JOIN TeacherOfficeRooms ORm ON ORm.OfficeRoomID = Te.OfficeRoomID
                    WHERE S.RollNumber = ?;
                """, (logged_in_roll,))
                rows = cursor.fetchall()
                conn.close()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to load teacher info: {e}")
                return

            if rows:
                for row in rows:
                    teacher_tree.insert("", tk.END, values=row)
            else:
                messagebox.showinfo("No Data", "No teacher info found.")

            teacher_tree.pack(pady=10, fill="both", expand=True)
            toggle_btn.config(text="Back to Timetable")
            is_showing_teacher = True

    # Connect button to toggle function
    toggle_btn.config(command=toggle_view)

    # Load initial timetable
    load_timetable()



#--------------------------------------------------------------------------------------------------------


def show_admin():
    
    global admin_title_label, admin_logout_btn

    clear_frame(center_frame)

    if admin_logout_btn:
        admin_logout_btn.destroy()
        admin_logout_btn = None 

    add_back_button()

    admin_title_label = tk.Label(root, text="Admin Panel", font=("Playfair Display", 32, "bold"), bg="#000000", fg="#00ffff")
    admin_title_label.place(relx=0.2, y=40, anchor="n")

   
    form_frame = tk.Frame(center_frame, bg="#0f0f0f", bd=0, relief="groove")  
    form_frame.pack(pady=80, padx=20)

   
    inner_frame = tk.Frame(form_frame, bg="#0f0f0f")
    inner_frame.pack(padx=30, pady=30)

    
    tk.Label(inner_frame, text="Username:", font=("Playfair Display", 18), bg="#0f0f0f", fg="white")\
        .grid(row=0, column=0, pady=15, padx=10, sticky="w")
    
    username_entry = tk.Entry(inner_frame, font=("Segoe UI", 15), width=25)
    username_entry.grid(row=0, column=1, pady=15, padx=10)

   
    tk.Label(inner_frame, text="Password:", font=("Playfair Display", 18), bg="#0f0f0f", fg="white")\
        .grid(row=1, column=0, pady=15, padx=10, sticky="w")
    
    password_entry = tk.Entry(inner_frame, font=("Segoe UI", 15), show="*", width=25)
    password_entry.grid(row=1, column=1, pady=15, padx=10)

    login_btn = tk.Button(inner_frame, text="Login", font=("Playfair Display", 13, "bold"), bg="#0078d7", fg="white", padx=12, pady=10, bd=0, width=10,command=lambda: admin_setting(username_entry.get(), password_entry.get()))
    login_btn.grid(row=2, column=0, columnspan=2, pady=(20, 10))



#--------------------------------------------------------------------------------------------------------


def admin_setting(username, password):
    conn = sqlite3.connect("timetable.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM Admins WHERE Username = ? AND Password = ?", (username, password))
    admin = cur.fetchone()
    conn.close()

    if admin:
        global back_btn, admin_title_label, admin_frame, admin_logout_btn

        clear_frame(center_frame)
        center_frame.pack_forget()

        if back_btn:
            back_btn.destroy()
            back_btn = None
        if admin_title_label:
            admin_title_label.destroy()
            admin_title_label = None

        admin_frame = tk.Frame(root, bg="#0f0f0f")
        admin_frame.pack(fill="both", expand=True)

        
        def logout_admin():
            admin_frame.destroy()
            center_frame.place(relx=0.5, rely=0.5, anchor="center")
            clear_frame(center_frame)
            show_admin()


        admin_logout_btn = tk.Button(root, text="Logout", command=logout_admin,
                                     font=("Segoe UI", 10, "bold"), bg="#0078d7", fg="white", bd=0)
        admin_logout_btn.place(relx=0.97, rely=0.02, anchor="ne")

        # Sidebar
        sidebar = tk.Frame(admin_frame, bg="#000000", width=200)
        sidebar.pack(side="left", fill="y")

        # Main content area
        content_area = tk.Frame(admin_frame, bg="#000000")
        content_area.pack(side="right", fill="both", expand=True)

        tk.Label(content_area, text=f"Welcome, {username}!", font=("Playfair Display", 24),
                 bg="#000000", fg="white").pack(pady=20)



        def clear_content():
            for widget in content_area.winfo_children():
                widget.destroy()

        #--------------------------------------------------


        def load_dashboard():
            clear_content()

            # Heading
            tk.Label(content_area, text="📊 Dashboard Overview", font=("Playfair Display", 20), bg="#000000", fg="white").pack(pady=(70, 50))

            # Frame for stats
            stats_frame = tk.Frame(content_area, bg="#000000")
            stats_frame.pack(pady=20)

            # Function to get counts
            def get_count(table_name):
                try:
                    conn = sqlite3.connect("timetable.db")
                    cur = conn.cursor()
                    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cur.fetchone()[0]
                    conn.close()
                    return count
                except:
                    return "N/A"

            # Get stats
            student_count = get_count("Students")
            teacher_count = get_count("Teachers")
            course_count = get_count("Courses")
            room_count = get_count("Rooms")

            # Stats list
            stats = [
                ("👨‍🎓 Total Students", student_count, "#00bfff"),
                ("👩‍🏫 Total Teachers", teacher_count, "#32cd32"),
                ("📚 Total Courses", course_count, "#ffa500"),
                ("🏫 Total Rooms", room_count, "#ff69b4")
            ]

            
            for index, (label, count, color) in enumerate(stats):
                row = index // 2     # 0 for first two, 1 for last two
                column = index % 2   # 0 and 1 for each row
                box = tk.Frame(stats_frame, bg=color, padx=40, pady=30)
                box.grid(row=row, column=column, padx=40, pady=30)

                tk.Label(box, text=label, font=("Playfair Display", 13, "bold"), bg=color, fg="white").pack()
                tk.Label(box, text=str(count), font=("Playfair Display", 20, "bold"), bg=color, fg="white").pack()



        #--------------------------------------------------


        def load_manage_students():
            clear_content()

            # 🏷️ Heading
            tk.Label(content_area, text="🎓 Manage Students", font=("Playfair Display", 20), bg="#000000", fg="white").pack(pady=(30, 20))

            # 📦 Frame for student table
            table_frame = tk.Frame(content_area, bg="#000000")
            table_frame.pack(fill=tk.BOTH, expand=True, padx=20)
            
            style = ttk.Style()
            style.theme_use("default")
            style.configure("Custom.Treeview",
                            background="#333333",
                            foreground="white",
                            fieldbackground="#333333",
                            font=("Segoe UI", 10))
            style.map("Custom.Treeview", background=[("selected", "#0078d7")])
            
            columns = ("StudentID", "RollNumber", "StudentName", "SectionName")
            global student_table
            student_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

            # 🔤 Headings and Column Widths
            headings = ["ID", "Roll No.", "Name", "Section"]
            col_widths = [60, 100, 200, 120]
            for col, head, width in zip(columns, headings, col_widths):
                student_table.heading(col, text=head)
                student_table.column(col, width=width, anchor="center")

            # 📜 Scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=student_table.yview)
            student_table.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            student_table.pack(fill="both", expand=True)

            # 🎛️ Buttons
            btn_frame = tk.Frame(content_area, bg="#000000")
            btn_frame.pack(pady=20)

            actions = [
                ("Add Student", add_student_window),
                ("Edit Student", edit_student_window),
                ("Delete Student", delete_student),
                ("Assign Class", assign_class_window),
                ("Deleted Log", view_deleted_log_window)
            ]

            for text, cmd in actions:
                tk.Button(btn_frame, text=text, font=("Segoe UI", 10), command=cmd,
                          bg="#0078D7", fg="white", padx=10, pady=5).pack(side=tk.LEFT, padx=10)

            load_students_data()
        



        def load_students_data():
            try:
                conn = sqlite3.connect("timetable.db")
                cur = conn.cursor()

                query = """
                SELECT s.StudentID, s.RollNumber, s.StudentName, sec.SectionName
                FROM Students s
                LEFT JOIN Sections sec ON s.SectionID = sec.SectionID
                """
                cur.execute(query)
                rows = cur.fetchall()

                for item in student_table.get_children():
                    student_table.delete(item)

                for row in rows:
                    student_table.insert("", tk.END, values=row)
        
                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", f"Error loading students: {e}")




        def add_student_window():
            add_window = tk.Toplevel(content_area)
            add_window.title("Add New Student")
            add_window.geometry("400x300")
            add_window.config(bg="#333333")

            tk.Label(add_window, text="Add New Student", font=("Playfair Display", 18), bg="#333333", fg="white").pack(pady=20)

            # Entry Fields
            tk.Label(add_window, text="Roll Number", font=("Segoe UI", 10), bg="#333333", fg="white").pack(pady=(5, 2))
            roll_no_entry = tk.Entry(add_window, font=("Segoe UI", 12), width=30)
            roll_no_entry.pack(pady=(0, 10))

            tk.Label(add_window, text="Name", font=("Segoe UI", 10), bg="#333333", fg="white").pack(pady=(5, 2))
            name_entry = tk.Entry(add_window, font=("Segoe UI", 12), width=30)
            name_entry.pack(pady=(0, 10))

            tk.Label(add_window, text="Section", font=("Segoe UI", 10), bg="#333333", fg="white").pack(pady=(5, 2))
            section_entry = tk.Entry(add_window, font=("Segoe UI", 12), width=30)
            section_entry.pack(pady=(0, 10))



            def save_student():
                roll_no = roll_no_entry.get()
                name = name_entry.get()
                section = section_entry.get()

                # Input Validation
                if not roll_no or not name or not section:
                    messagebox.showerror("Input Error", "Please fill in all fields")
                    return

                try:
                    with sqlite3.connect("timetable.db") as conn:
                        cur = conn.cursor()
                        cur.execute("INSERT INTO Students (RollNumber, StudentName, SectionID) VALUES (?, ?, ?)", (roll_no, name, section))
                        conn.commit()


                    messagebox.showinfo("Success", "Student added successfully!")
                    add_window.destroy()  # Close the window
                    content_area.after(100, load_students_data)   # Reload data

                except Exception as e:
                    messagebox.showerror("Database Error", f"Error adding student: {e}")

            # Save Button
            tk.Button(add_window, text="Save", font=("Segoe UI", 12, "bold"), bg="#0078d7", fg="white", command=save_student).pack(pady=20)


        def edit_student_window():
            selected_item = student_table.selection()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select a student to edit.")
                return

            student_id = student_table.item(selected_item[0], "values")[0]
            roll_no = student_table.item(selected_item[0], "values")[1]
            name = student_table.item(selected_item[0], "values")[2]
            section = student_table.item(selected_item[0], "values")[3]

            edit_window = tk.Toplevel(content_area)
            edit_window.title("Edit Student")
            edit_window.geometry("400x300")
            edit_window.config(bg="#333333")

            tk.Label(edit_window, text="Edit Student", font=("Playfair Display", 18), bg="#333333", fg="white").pack(pady=20)

            # Entry Fields
            tk.Label(edit_window, text="Roll Number", font=("Segoe UI", 10), bg="#333333", fg="white").pack(pady=(5, 2))
            roll_no_entry = tk.Entry(edit_window, font=("Segoe UI", 12), width=30)
            roll_no_entry.insert(0, roll_no)
            roll_no_entry.pack(pady=(0, 10))
            
            tk.Label(edit_window, text="Name", font=("Segoe UI", 10), bg="#333333", fg="white").pack(pady=(5, 2))
            name_entry = tk.Entry(edit_window, font=("Segoe UI", 12), width=30)
            name_entry.insert(0, name)
            name_entry.pack(pady=(0, 10))

            tk.Label(edit_window, text="Section", font=("Segoe UI", 10), bg="#333333", fg="white").pack(pady=(5, 2))
            section_entry = tk.Entry(edit_window, font=("Segoe UI", 12), width=30)
            section_entry.insert(0, section)
            section_entry.pack(pady=(0, 10))

            def update_student():
                updated_roll_no = roll_no_entry.get()
                updated_name = name_entry.get()
                updated_section = section_entry.get()

                if not updated_roll_no or not updated_name or not updated_section:
                    messagebox.showerror("Input Error", "Please fill in all fields")
                    return

                try:
                    conn = sqlite3.connect("timetable.db")
                    cur = conn.cursor()

                    cur.execute("""
                        UPDATE Students 
                        SET RollNumber = ?, StudentName = ?, SectionID = ?
                        WHERE StudentID = ?
                    """, (updated_roll_no, updated_name, updated_section, student_id))
                    conn.commit()
                    conn.close()

                    messagebox.showinfo("Success", "Student details updated successfully!")
                    edit_window.destroy()  # Close the window
                    load_students_data()    # Reload data
                except Exception as e:
                    messagebox.showerror("Database Error", f"Error updating student: {e}")

            # Update Button
            tk.Button(edit_window, text="Update", font=("Segoe UI", 12, "bold"), bg="#0078d7", fg="white", command=update_student).pack(pady=20)


        def delete_student():
            selected_item = student_table.selection()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select a student to delete.")
                return

            student_id = student_table.item(selected_item[0], "values")[0]

            try:
                conn = sqlite3.connect("timetable.db")
                cur = conn.cursor()

                # Get student details before deletion
                cur.execute("SELECT RollNumber, StudentName, SectionID FROM Students WHERE StudentID = ?", (student_id,))
                student = cur.fetchone()
            
                cur.execute("SELECT AdminID FROM Admins WHERE Username = ?", (username,))
                admin_id = cur.fetchone()
            
                if student:
                    roll_no, name, section = student

                     # Insert into DeletedStudents table
                    cur.execute("""
                        INSERT INTO DeletedStudents (StudentID,RollNumber, StudentName, SectionID,DeletedByAdminID)
                        VALUES (?, ?, ?)
                    """, (student_id,roll_no, name, section,admin_id))
                    conn.commit()

                    # Delete from Students table
                    cur.execute("DELETE FROM Students WHERE StudentID = ?", (student_id,))
                    conn.commit()

                    messagebox.showinfo("Success", "Student deleted successfully!")
                    load_students_data()  # Reload data
                else:
                    messagebox.showerror("Error", "Student not found.")

                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", f"Error deleting student: {e}")





        def assign_class_window():
            selected_item = student_table.selection()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select a student to assign a class.")
                return

            student_id = student_table.item(selected_item[0], "values")[0]

            assign_window = tk.Toplevel(content_area)
            assign_window.title("Assign Class to Student")
            assign_window.geometry("400x350")
            assign_window.config(bg="#333333")

            tk.Label(assign_window, text="Assign Class", font=("Playfair Display", 18), bg="#333333", fg="white").pack(pady=15)

            # Dropdowns
            tk.Label(assign_window, text="Select Offering", bg="#333333", fg="white").pack()
            offering_combo = ttk.Combobox(assign_window, width=40, state="readonly")
            offering_combo.pack(pady=5)

            tk.Label(assign_window, text="Day ID (1=Mon..7)", bg="#333333", fg="white").pack()
            day_entry = tk.Entry(assign_window, width=40)
            day_entry.pack(pady=5)

            tk.Label(assign_window, text="Slot ID (1..n)", bg="#333333", fg="white").pack()
            slot_entry = tk.Entry(assign_window, width=40)
            slot_entry.pack(pady=5)

            tk.Label(assign_window, text="Room ID", bg="#333333", fg="white").pack()
            room_entry = tk.Entry(assign_window, width=40)
            room_entry.pack(pady=5)

            tk.Label(assign_window, text="Class Type ID (1=Lecture, 2=Lab)", bg="#333333", fg="white").pack()
            class_type_entry = tk.Entry(assign_window, width=40)
            class_type_entry.pack(pady=5)

            # Load offerings into dropdown
            try:
                with sqlite3.connect("timetable.db") as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT co.OfferingID, c.CourseName || " by " || t.TeacherName
                        FROM CourseOfferings co
                        JOIN Courses c ON co.CourseID = c.CourseID
                        JOIN Teachers t ON co.TeacherID = t.TeacherID
                    """)
                    offerings = cur.fetchall()
                    offering_combo["values"] = [f"{oid} - {desc}" for oid, desc in offerings]
            except Exception as e:
                messagebox.showerror("Error", f"Could not load course offerings: {e}")
                assign_window.destroy()
                return

            def assign_class():
                try:
                    if not offering_combo.get().strip():
                        messagebox.showwarning("Missing Info", "Please select an offering.")
                        return

                    offering_id = int(offering_combo.get().split(" - ")[0])
                    day_id = int(day_entry.get())
                    slot_id = int(slot_entry.get())
                    room_id = int(room_entry.get())
                    class_type_id = int(class_type_entry.get())

                    with sqlite3.connect("timetable.db") as conn:
                        cur = conn.cursor()

                        # Check if student already has a class at this time
                        cur.execute("""
                            SELECT 1 FROM class_schedule
                            WHERE student_id = ? AND day_id = ? AND timeslot_id = ?
                        """, (student_id, day_id, slot_id))
                        if cur.fetchone():
                            messagebox.showerror("Conflict", "Student already has a class at this time.")
                            return

                        # Check if room is already used at this time
                        cur.execute("""
                            SELECT 1 FROM ClassTimes
                            WHERE DayID = ? AND SlotID = ? AND RoomID = ?
                        """, (day_id, slot_id, room_id))
                        if cur.fetchone():
                            messagebox.showerror("Conflict", "Room is already booked at this time.")
                            return

                        # Check or create ClassTime
                        cur.execute("""
                            SELECT ClassTimeID FROM ClassTimes
                            WHERE OfferingID = ? AND DayID = ? AND SlotID = ? AND RoomID = ? AND ClassTypeID = ?
                        """, (offering_id, day_id, slot_id, room_id, class_type_id))
                        result = cur.fetchone()

                        if result:
                            class_time_id = result[0]
                        else:
                            cur.execute("""
                                INSERT INTO ClassTimes (OfferingID, DayID, SlotID, RoomID, ClassTypeID)
                                VALUES (?, ?, ?, ?, ?)
                            """, (offering_id, day_id, slot_id, room_id, class_type_id))
                            class_time_id = cur.lastrowid

                        # Get Course, Teacher, Section info from Offering
                        cur.execute("""
                            SELECT CourseID, TeacherID, SectionID
                            FROM CourseOfferings
                            WHERE OfferingID = ?
                        """, (offering_id,))
                        offering = cur.fetchone()

                        if not offering:
                            messagebox.showerror("Error", "Offering not found.")
                            return

                        course_id, teacher_id, section_id = offering

                        # Insert into class_schedule
                        cur.execute("""
                            INSERT INTO class_schedule (student_id, course_id, teacher_id, room_id, section_id, day_id, timeslot_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (student_id, course_id, teacher_id, room_id, section_id, day_id, slot_id))

                        conn.commit()
                        messagebox.showinfo("Success", "Class assigned successfully.")
                        assign_window.destroy()

                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter valid numeric values in all fields.")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not assign class: {e}")

            tk.Button(assign_window, text="Assign", font=("Segoe UI", 12), bg="#0078d7", fg="white", command=assign_class).pack(pady=20)

     
        def view_deleted_log_window():
            log_window = tk.Toplevel(content_area)
            log_window.title("Deleted Students Log")
            log_window.geometry("1000x450")
            log_window.config(bg="#000000")

            tk.Label(log_window, text="🗑️ Deleted Students Log", font=("Playfair Display", 18), bg="#000000", fg="white").pack(pady=20)

            # Frame for table
            table_frame = tk.Frame(log_window, bg="#000000")
            table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            # Columns
            columns = ("DeletedID", "RollNumber", "StudentName", "SectionID", "DeletedAt", "DeletedBy")
            tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    # Headings
            tree.heading("DeletedID", text="ID")
            tree.heading("RollNumber", text="Roll Number")
            tree.heading("StudentName", text="Name")
            tree.heading("SectionID", text="Section")
            tree.heading("DeletedAt", text="Deleted At")
            tree.heading("DeletedBy", text="Deleted By (Admin)")

    # Column widths
            tree.column("DeletedID", width=50, anchor="center")
            tree.column("RollNumber", width=120, anchor="center")
            tree.column("StudentName", width=180, anchor="center")
            tree.column("SectionID", width=80, anchor="center")
            tree.column("DeletedAt", width=180, anchor="center")
            tree.column("DeletedBy", width=180, anchor="center")

    # Scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(fill="both", expand=True)

            # Load data with admin name
            try:
                with sqlite3.connect("timetable.db", timeout=5) as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT 
                            ds.DeletedID,
                            ds.RollNumber,
                            ds.StudentName,
                            ds.SectionID,
                            ds.DeletedAt,
                            IFNULL(a.Username, 'Unknown') AS DeletedBy
                        FROM DeletedStudents ds
                        LEFT JOIN Admins a ON ds.DeletedByAdminID = a.AdminID
                        ORDER BY ds.DeletedAt DESC
                    """)
                    rows = cur.fetchall()
        
                for row in rows:
                    tree.insert("", tk.END, values=row)
        
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to load deleted students log:\n{e}")


        #--------------------------------------------------

        def load_manage_teachers():

            clear_content()

            # 🏷️ Heading
            tk.Label(content_area, text="👨‍🏫 Manage Teachers", font=("Playfair Display", 20), bg="#000000", fg="white").pack(pady=(30, 20), anchor="w", padx=40)

            # 📦 Frame for teacher table
            table_frame = tk.Frame(content_area, bg="#000000")
            table_frame.pack(fill=tk.BOTH, expand=True, padx=40)

            style = ttk.Style()
            style.theme_use("default")
            style.configure("Custom.Treeview",
                            background="#333333",
                            foreground="white",
                            fieldbackground="#333333",
                            font=("Segoe UI", 10))
            style.map("Custom.Treeview", background=[("selected", "#0078d7")])

            columns = ("TeacherID", "TeacherName", "AssignedCourses")
            global teacher_table
            teacher_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

            # 🔤 Headings and Column Widths
            teacher_table.heading("TeacherID", text="ID")
            teacher_table.heading("TeacherName", text="Name")
            teacher_table.heading("AssignedCourses", text="Courses")

            teacher_table.column("TeacherID", width=60, anchor="center")
            teacher_table.column("TeacherName", width=200, anchor="center")
            teacher_table.column("AssignedCourses", width=400, anchor="w")

            # 📜 Scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=teacher_table.yview)
            teacher_table.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            teacher_table.pack(fill="both", expand=True)

            # 🎛️ Buttons
            btn_frame = tk.Frame(content_area, bg="#000000")
            btn_frame.pack(pady=20)

            actions = [
                ("Edit Teacher", edit_teacher_window),
                ("Delete Teacher", delete_teacher)
            ]

            for text, cmd in actions:
                tk.Button(btn_frame, text=text, font=("Segoe UI", 10), command=cmd,
                          bg="#0078D7", fg="white", padx=10, pady=5).pack(side=tk.LEFT, padx=10)

            load_teachers_data()


        def load_teachers_data():
            try:
                conn = sqlite3.connect("timetable.db")
                cur = conn.cursor()

                query = """
                SELECT 
                    t.TeacherID,
                    t.TeacherName,
                    IFNULL(GROUP_CONCAT(c.CourseName, ', '), 'No Courses')
                FROM Teachers t
                LEFT JOIN CourseOfferings co ON t.TeacherID = co.TeacherID
                LEFT JOIN Courses c ON co.CourseID = c.CourseID
                GROUP BY t.TeacherID
                """
                cur.execute(query)
                rows = cur.fetchall()

                for item in teacher_table.get_children():
                    teacher_table.delete(item)

                for row in rows:
                    teacher_table.insert("", tk.END, values=row)

                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", f"Error loading teachers: {e}")
        


        def edit_teacher_window():
            selected_item = teacher_table.selection()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select a teacher to edit.")
                return

            teacher_id = teacher_table.item(selected_item[0], "values")[0]
            teacher_name = teacher_table.item(selected_item[0], "values")[1]

            edit_window = tk.Toplevel(content_area)
            edit_window.title("Edit Teacher")
            edit_window.geometry("400x250")
            edit_window.config(bg="#333333")

            tk.Label(edit_window, text="Edit Teacher", font=("Playfair Display", 18), bg="#333333", fg="white").pack(pady=20)

            tk.Label(edit_window, text="Name", font=("Segoe UI", 10), bg="#333333", fg="white").pack(pady=(5, 2))
            name_entry = tk.Entry(edit_window, font=("Segoe UI", 12), width=30)
            name_entry.insert(0, teacher_name)
            name_entry.pack(pady=(0, 10))

            def update_teacher():
                updated_name = name_entry.get()

                if not updated_name:
                    messagebox.showerror("Input Error", "Please enter a name.")
                    return

                try:
                    conn = sqlite3.connect("timetable.db")
                    cur = conn.cursor()

                    cur.execute("UPDATE Teachers SET TeacherName = ? WHERE TeacherID = ?", (updated_name, teacher_id))
                    conn.commit()
                    conn.close()

                    messagebox.showinfo("Success", "Teacher updated successfully!")
                    edit_window.destroy()
                    load_teachers_data()
                except Exception as e:
                    messagebox.showerror("Database Error", f"Error updating teacher: {e}")

            tk.Button(edit_window, text="Update", font=("Segoe UI", 12, "bold"), bg="#0078d7", fg="white", command=update_teacher).pack(pady=20)


        def delete_teacher():
            selected_item = teacher_table.selection()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select a teacher to delete.")
                return

            teacher_id = teacher_table.item(selected_item[0], "values")[0]

            try:
                conn = sqlite3.connect("timetable.db")
                cur = conn.cursor()

                # Check if teacher is assigned to any course
                cur.execute("SELECT COUNT(*) FROM CourseOfferings WHERE TeacherID = ?", (teacher_id,))
                count = cur.fetchone()[0]

                if count > 0:
                    messagebox.showerror("Cannot Delete", "Teacher is assigned to one or more courses. Remove assignments first.")
                    return

                # Safe to delete
                cur.execute("DELETE FROM Teachers WHERE TeacherID = ?", (teacher_id,))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Teacher deleted successfully!")
                load_teachers_data()
            except Exception as e:
                messagebox.showerror("Database Error", f"Error deleting teacher: {e}")


        #--------------------------------------------------

        def load_manage_courses():
            clear_content()
            
            tk.Label(
                    content_area, 
                    text="📚 Manage Courses",  
                    font=("Playfair Display", 20), 
                    bg="#000000", 
                    fg="white"
            ).pack(pady=(50, 40))

            # Table Frame
            table_frame = tk.Frame(content_area)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=40)

            course_table = ttk.Treeview(
                        table_frame, 
                        columns=("CourseCode", "CourseName", "CreditHours", "Department"), 
                        show="headings"
            )

            course_table.heading("CourseCode", text="Course Code")
            course_table.heading("CourseName", text="Course Name")
            course_table.heading("CreditHours", text="Credit Hours")
            course_table.heading("Department", text="Department")

            course_table.column("CourseCode", width=100)
            course_table.column("CourseName", width=200)
            course_table.column("CreditHours", width=100)
            course_table.column("Department", width=150)

            course_table.pack(fill=tk.BOTH, expand=True)

            # Load course data
            try:
                        conn = sqlite3.connect("timetable.db")
                        cur = conn.cursor()

                        cur.execute("""
                                    SELECT CourseCode, CourseName, CreditHours, Departments.DepartmentName
                                    FROM Courses
                                    JOIN Departments ON Courses.DepartmentID = Departments.DepartmentID
                                    ORDER BY CourseCode ASC
                        """)

                        for row in cur.fetchall():
                                    course_table.insert("", tk.END, values=row)

                        conn.close()

            except Exception as e:
                        messagebox.showerror("Database Error", f"Error loading courses: {e}")


        #--------------------------------------------------


        def load_room_schedule():
            clear_content()

            # 🏷️ Heading
            tk.Label(content_area, text="🏢 Room Scheduling", font=("Playfair Display", 20),
             bg="#000000", fg="white").pack(pady=(30, 20))  # Top margin

            # 📦 Table Frame
            table_frame = tk.Frame(content_area, bg="#000000")
            table_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))  # Padding at bottom

            # 🧱 Treeview setup
            columns = ("Room", "Day", "Time Slot", "Course", "Teacher", "Section")

            room_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15, style="Custom.Treeview")

            headings = ["Room", "Day", "Time Slot", "Course", "Teacher", "Section"]
            widths = [120, 100, 130, 200, 160, 80]

            for col, heading, width in zip(columns, headings, widths):
                room_table.heading(col, text=heading)
                room_table.column(col, width=width, anchor="center")

            # 📜 Scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=room_table.yview)
            room_table.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            room_table.pack(fill="both", expand=True)

            #  Treeview style (assuming globally defined)
            style = ttk.Style()
            style.theme_use("default")
            style.configure("Custom.Treeview",
                    background="#333333",
                    foreground="white",
                    fieldbackground="#333333",
                    font=("Segoe UI", 10))
            style.map("Custom.Treeview", background=[("selected", "#0078d7")])

            # 📥 Load data from database
            try:
                conn = sqlite3.connect("timetable.db")
                cur = conn.cursor()

                query = """
                SELECT 
                    r.RoomName,
                    d.DayName,
                    ts.SlotName,
                    c.CourseName,
                    t.TeacherName,
                    s.SectionName
                FROM ClassTimes ct
                JOIN CourseOfferings co ON ct.OfferingID = co.OfferingID
                JOIN Courses c ON co.CourseID = c.CourseID
                JOIN Teachers t ON co.TeacherID = t.TeacherID
                JOIN Rooms r ON ct.RoomID = r.RoomID
                JOIN Days d ON ct.DayID = d.DayID
                JOIN TimeSlots ts ON ct.SlotID = ts.SlotID
                JOIN Sections s ON co.SectionID = s.SectionID
                ORDER BY r.RoomName, d.DayID, ts.SlotID
                """

                cur.execute(query)
                rows = cur.fetchall()

                for row in rows:
                    room_table.insert("", tk.END, values=row)

                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load room schedule: {e}")



        #--------------------------------------------------


        def load_timetable():
            clear_content()

            # 🏷️ Heading
            tk.Label(content_area, text="🗓️ View & Manage Timetables", font=("Playfair Display", 20),
             bg="#000000", fg="white").pack(pady=(30, 20))

            # 📦 Table Frame
            table_frame = tk.Frame(content_area, bg="#000000")
            table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            style = ttk.Style()
            style.theme_use("default")
            style.configure("Custom.Treeview",
                            background="#333333",
                            foreground="white",
                            fieldbackground="#333333",
                            font=("Segoe UI", 10))
            style.map("Custom.Treeview", background=[("selected", "#0078d7")])

            # 🧱 Treeview setup
            columns = ("ClassTimeID", "CourseCode", "CourseName", "TeacherName", "RoomName", "DayName", "SlotName", "ClassTypeName")

            global timetable_table
            timetable_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

            # 🔠 Column headings
            headings = [
                "ID", "Course Code", "Course Name", "Teacher", "Room", "Day", "Time Slot", "Class Type"
            ]
            column_settings = {
                "ClassTimeID": 80,
                "CourseCode": 100,
                "CourseName": 180,
                "TeacherName": 150,
                "RoomName": 100,
                "DayName": 100,
                "SlotName": 130,
                "ClassTypeName": 120
            }

            for col, heading in zip(columns, headings):
                timetable_table.heading(col, text=heading)
                timetable_table.column(col, width=column_settings[col], anchor="center", stretch=True)


            # 📜 Add scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=timetable_table.yview)
            timetable_table.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            timetable_table.pack(fill="both", expand=True)

            # ⬇️ Load data
            load_timetable_data()


        def load_timetable_data():
            try:
                conn = sqlite3.connect("timetable.db")
                cur = conn.cursor()

                query = """
                SELECT 
                    ct.ClassTimeID,
                    c.CourseCode,
                    c.CourseName,
                    t.TeacherName,
                    r.RoomName,
                    d.DayName,
                    ts.SlotName,
                    cl.ClassTypeName
                FROM ClassTimes ct
                JOIN CourseOfferings co ON ct.OfferingID = co.OfferingID
                JOIN Courses c ON co.CourseID = c.CourseID
                JOIN Teachers t ON co.TeacherID = t.TeacherID
                JOIN Rooms r ON ct.RoomID = r.RoomID
                JOIN Days d ON ct.DayID = d.DayID
                JOIN TimeSlots ts ON ct.SlotID = ts.SlotID
                JOIN ClassTypes cl ON ct.ClassTypeID = cl.ClassTypeID
                """

                cur.execute(query)
                records = cur.fetchall()

                # 🧹 Clear old data
                for row in timetable_table.get_children():
                    timetable_table.delete(row)

                # ➕ Insert rows
                for row in records:
                    timetable_table.insert("", tk.END, values=row)

                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", f"Error loading timetable: {e}")




        #--------------------------------------------------


        def load_admin_settings():
             
            clear_content()

            # Heading
            tk.Label(content_area, text="⚙️ Admin Account Settings", font=("Playfair Display", 20), bg="#000000", fg="white").pack(pady=(50, 120))

            # Sub-heading
            tk.Label(content_area, text="➕ Add New Admin", font=("Playfair Display", 18, "bold"), bg="#0f0f0f", fg="#00ffff").pack(pady=(10, 15))

            # Form frame
            form_frame = tk.Frame(content_area, bg="#0f0f0f")
            form_frame.pack(pady=40)

        # Username
            tk.Label(form_frame, text="Username:", font=("Playfair Display", 18), bg="#0f0f0f", fg="white").grid(row=0, column=0, sticky="w", padx=10, pady=10)
            username_entry = tk.Entry(form_frame, font=("Segoe UI", 14), width=30)
            username_entry.grid(row=0, column=1, padx=10, pady=10)

            # Password
            tk.Label(form_frame, text="Password:", font=("Playfair Display", 18), bg="#0f0f0f", fg="white").grid(row=1, column=0, sticky="w", padx=10, pady=10)
            password_entry = tk.Entry(form_frame, font=("Segoe UI", 14), width=30, show="*")
            password_entry.grid(row=1, column=1, padx=10, pady=10)

    # Add button function
            def add_admin():
                username = username_entry.get().strip()
                password = password_entry.get().strip()

                if not username or not password:
                    messagebox.showwarning("Input Error", "Both fields are required.")
                    return

                try:
                    conn = sqlite3.connect("timetable.db")
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM Admins WHERE Username = ?", (username,))
                    if cur.fetchone():
                        messagebox.showerror("Duplicate", "Username already exists.")
                    else:
                        cur.execute("INSERT INTO Admins (Username, Password) VALUES (?, ?)", (username, password))
                        conn.commit()
                        messagebox.showinfo("Success", f"Admin '{username}' added successfully.")
                        username_entry.delete(0, tk.END)
                        password_entry.delete(0, tk.END)
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Error: {e}")
                finally:
                    conn.close()

    # Add button
            tk.Button(content_area, text="Add Admin", font=("Segoe UI", 12, "bold"), bg="#0078d7", fg="white", padx=15, pady=5, command=add_admin).pack(pady=15)


        #--------------------------------------------------            


        button_style = {
            "font": ("Segoe UI", 13, "bold"),
            "bg": "#0093dd",
            "fg": "white",
            "bd": 0.5,
            "width": 20,
            "anchor": "w",
            "justify": "left",
            "padx": 25,  # internal left padding
        }

# Add some padding above the first button
        tk.Button(sidebar, text="📊 Dashboard", command=load_dashboard, **button_style).pack(pady=(110, 10), anchor="w", ipady=6)
        tk.Button(sidebar, text="🎓 Manage Students", command=load_manage_students, **button_style).pack(pady=10, anchor="w", ipady=6)
        tk.Button(sidebar, text="👨‍🏫 Manage Teachers", command=load_manage_teachers, **button_style).pack(pady=10, anchor="w", ipady=6)
        tk.Button(sidebar, text="📚 See Courses", command=load_manage_courses, **button_style).pack(pady=10, anchor="w", ipady=6)
        tk.Button(sidebar, text="🏢 Room Scheduling", command=load_room_schedule, **button_style).pack(pady=10, anchor="w", ipady=6)
        tk.Button(sidebar, text="🗓️ Timetable", command=load_timetable, **button_style).pack(pady=10, anchor="w", ipady=6)
        tk.Button(sidebar, text="⚙️ Admin Settings", command=load_admin_settings, **button_style).pack(pady=10, anchor="w", ipady=6)

    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")






#--------------------------------------------------------------------------------------------------------



def add_back_button():
    global back_btn
    back_btn = tk.Button(root, text="Back", command=show_entry, bg="#0093dd", fg="white", font=("Segoe UI", 10), bd=0)
    back_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)


def student_logout_button():
    global student_logout_btn
    student_logout_btn = tk.Button(root, text="Logout", command=show_student, bg="#0093dd", fg="white", font=("Segoe UI", 10), bd=0)
    student_logout_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)


def admin_logout_button():
    global admin_logout_btn
    admin_logout_btn = tk.Button(root, text="Logout", command=show_admin, bg="#0093dd", fg="white", font=("Segoe UI", 10), bd=0)
    admin_logout_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
    


#--------------------------------------------------------------------------------------------------------



root = tk.Tk()
root.title("Modern Timetable Manager - Entry")
root.geometry("800x600")
root.configure(bg="#000000")
root.attributes('-fullscreen', True)

center_frame = tk.Frame(root, bg="#000000")
center_frame.place(relx=0.5, rely=0.5, anchor="center")

show_entry()

def exit_fullscreen(event):
    root.attributes('-fullscreen', False)

root.bind("<Escape>", exit_fullscreen)
root.mainloop()



#--------------------------------------------------------------------------------------------------------

