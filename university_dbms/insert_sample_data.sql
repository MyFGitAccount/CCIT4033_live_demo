-- insert_sample_data.sql
-- Insert sample departments
INSERT OR IGNORE INTO Department (DeptName, DeptCode, Budget, Location, IsActive) VALUES
('Computer Science', 'CS', 500000, 'Building A', 1),
('Mathematics', 'MATH', 300000, 'Building B', 1),
('Physics', 'PHY', 400000, 'Building C', 1),
('Business Administration', 'BA', 450000, 'Building D', 1);

-- Insert sample teachers
INSERT OR IGNORE INTO Teacher (FirstName, LastName, Email, DepartmentID, Status, HireDate, IsDeleted) VALUES
('John', 'Smith', 'john.smith@university.edu', 1, 'Active', '2015-08-15', 0),
('Sarah', 'Johnson', 'sarah.johnson@university.edu', 1, 'Active', '2018-01-10', 0),
('Michael', 'Brown', 'michael.brown@university.edu', 2, 'Active', '2010-09-01', 0),
('Emily', 'Davis', 'emily.davis@university.edu', 3, 'Active', '2019-06-20', 0);

-- Insert sample courses
INSERT OR IGNORE INTO Course (CourseCode, CourseName, Credits, DepartmentID, IsActive, IsDeleted) VALUES
('CS101', 'Introduction to Programming', 3, 1, 1, 0),
('CS201', 'Data Structures', 3, 1, 1, 0),
('CS301', 'Database Systems', 3, 1, 1, 0),
('MATH101', 'Calculus I', 4, 2, 1, 0),
('PHY101', 'Physics I', 4, 3, 1, 0),
('BA101', 'Principles of Management', 3, 4, 1, 0);

-- Insert sample classrooms
INSERT OR IGNORE INTO Classroom (RoomNumber, Building, Capacity, Type) VALUES
('101', 'Building A', 50, 'Lecture'),
('102', 'Building A', 40, 'Lab'),
('201', 'Building B', 60, 'Lecture'),
('301', 'Building C', 30, 'Seminar');

-- Insert sample students
INSERT OR IGNORE INTO Student (StudentNumber, FirstName, LastName, NationalID, Country, Email, DepartmentID, EnrollmentDate, IsDeleted) VALUES
('STU20240001', 'Alice', 'Williams', 'ID001', 'USA', 'alice@student.edu', 1, '2024-09-01', 0),
('STU20240002', 'Bob', 'Jones', 'ID002', 'Canada', 'bob@student.edu', 1, '2024-09-01', 0),
('STU20240003', 'Carol', 'Miller', 'ID003', 'UK', 'carol@student.edu', 2, '2024-09-01', 0);
