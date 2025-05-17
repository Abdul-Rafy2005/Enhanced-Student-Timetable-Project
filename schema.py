import sqlite3

conn = sqlite3.connect("timetable.db")
cur = conn.cursor()

cur.execute("PRAGMA foreign_keys = ON;")

cur.executescript("""
-- Departments
CREATE TABLE IF NOT EXISTS Departments (
    DepartmentID INTEGER PRIMARY KEY AUTOINCREMENT,
    DepartmentName TEXT NOT NULL
);

-- Sections
CREATE TABLE IF NOT EXISTS Sections (
    SectionID INTEGER PRIMARY KEY AUTOINCREMENT,
    SectionName TEXT NOT NULL,
    DepartmentID INTEGER,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Semesters
CREATE TABLE IF NOT EXISTS Semesters (
    SemesterID INTEGER PRIMARY KEY AUTOINCREMENT,
    SemesterName TEXT NOT NULL,
    StartDate DATE,
    EndDate DATE
);

-- Students
CREATE TABLE IF NOT EXISTS Students (
    StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
    RollNumber TEXT UNIQUE NOT NULL,
    StudentName TEXT NOT NULL,
    SectionID INTEGER,
    FOREIGN KEY (SectionID) REFERENCES Sections(SectionID) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Admins
CREATE TABLE IF NOT EXISTS Admins (
    AdminID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL,
    Password TEXT NOT NULL
);

-- DeletedStudents
CREATE TABLE IF NOT EXISTS DeletedStudents (
    DeletedID INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentID INTEGER,
    RollNumber TEXT,
    StudentName TEXT,
    SectionID INTEGER,
    DeletedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    DeletedByAdminID INTEGER,
    FOREIGN KEY (DeletedByAdminID) REFERENCES Admins(AdminID) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Courses
CREATE TABLE IF NOT EXISTS Courses (
    CourseID INTEGER PRIMARY KEY AUTOINCREMENT,
    CourseCode TEXT NOT NULL,
    CourseName TEXT NOT NULL,
    CreditHours INTEGER,
    DepartmentID INTEGER,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Teachers
CREATE TABLE IF NOT EXISTS Teachers (
    TeacherID INTEGER PRIMARY KEY AUTOINCREMENT,
    TeacherName TEXT NOT NULL,
    Email TEXT,
    DepartmentID INTEGER,
    OfficeRoomID INTEGER,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (OfficeRoomID) REFERENCES TeacherOfficeRooms(OfficeRoomID) ON DELETE SET NULL ON UPDATE CASCADE
);


-- TeacherOfficeRooms
CREATE TABLE IF NOT EXISTS TeacherOfficeRooms (
    OfficeRoomID INTEGER PRIMARY KEY AUTOINCREMENT,
    RoomName TEXT NOT NULL
);

-- TeacherOfficeAssignments
CREATE TABLE IF NOT EXISTS TeacherOfficeAssignments (
    TeacherID INTEGER,
    OfficeRoomID INTEGER,
    PRIMARY KEY (TeacherID, OfficeRoomID),
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (OfficeRoomID) REFERENCES TeacherOfficeRooms(OfficeRoomID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Rooms
CREATE TABLE IF NOT EXISTS Rooms (
    RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
    RoomName TEXT NOT NULL,
    RoomType TEXT CHECK(RoomType IN ('Lecture', 'Lab')),
    Capacity INTEGER
);

-- Days
CREATE TABLE IF NOT EXISTS Days (
    DayID INTEGER PRIMARY KEY AUTOINCREMENT,
    DayName TEXT NOT NULL
);

-- TimeSlots
CREATE TABLE IF NOT EXISTS TimeSlots (
    SlotID INTEGER PRIMARY KEY AUTOINCREMENT,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    SlotName TEXT
);

-- ClassTypes
CREATE TABLE IF NOT EXISTS ClassTypes (
    ClassTypeID INTEGER PRIMARY KEY AUTOINCREMENT,
    ClassTypeName TEXT NOT NULL
);

-- CourseOfferings
CREATE TABLE IF NOT EXISTS CourseOfferings (
    OfferingID INTEGER PRIMARY KEY AUTOINCREMENT,
    CourseID INTEGER,
    TeacherID INTEGER,
    SectionID INTEGER,
    SemesterID INTEGER,
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (SectionID) REFERENCES Sections(SectionID) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (SemesterID) REFERENCES Semesters(SemesterID) ON DELETE SET NULL ON UPDATE CASCADE
);

-- ClassTimes
CREATE TABLE IF NOT EXISTS ClassTimes (
    ClassTimeID INTEGER PRIMARY KEY AUTOINCREMENT,
    OfferingID INTEGER,
    RoomID INTEGER,
    DayID INTEGER,
    SlotID INTEGER,
    ClassTypeID INTEGER,
    FOREIGN KEY (OfferingID) REFERENCES CourseOfferings(OfferingID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (DayID) REFERENCES Days(DayID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (SlotID) REFERENCES TimeSlots(SlotID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ClassTypeID) REFERENCES ClassTypes(ClassTypeID) ON DELETE SET NULL ON UPDATE CASCADE
);

-- class_schedule (for per-student final schedules)
CREATE TABLE IF NOT EXISTS class_schedule (
    ScheduleID INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    course_id INTEGER,
    teacher_id INTEGER,
    room_id INTEGER,
    section_id INTEGER,
    day_id INTEGER,
    timeslot_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES Students(RollNumber) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Courses(CourseID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(TeacherID) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (room_id) REFERENCES Rooms(RoomID) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (section_id) REFERENCES Sections(SectionID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (day_id) REFERENCES Days(DayID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (timeslot_id) REFERENCES TimeSlots(SlotID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Trigger: Backup student before deletion
CREATE TRIGGER IF NOT EXISTS delete_student
BEFORE DELETE ON Students
BEGIN
    INSERT INTO DeletedStudents (StudentID, RollNumber, StudentName, SectionID, DeletedByAdminID)
    VALUES (OLD.StudentID, OLD.RollNumber, OLD.StudentName, OLD.SectionID, 1);
END;
""")

conn.commit()
conn.close()

print("Database schema created safely and successfully.")
