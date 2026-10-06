import os
import sqlite3
import random
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort

app = Flask(__name__)
app.secret_key = 'studenthub-secret-key-2026'

# Database configuration
DB_FOLDER = app.instance_path
DB_PATH = os.path.join(DB_FOLDER, 'studenthub.db')

def get_db_connection():
    os.makedirs(DB_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(DB_FOLDER, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            course TEXT NOT NULL,
            semester TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            gpa REAL DEFAULT 3.5,
            enrollment_date TEXT,
            dob TEXT,
            address TEXT,
            guardian_name TEXT,
            guardian_phone TEXT,
            bio TEXT
        )
    ''')
    conn.commit()

    # Check if table has data; if not, seed realistic records
    cursor.execute('SELECT COUNT(*) FROM students')
    count = cursor.fetchone()[0]
    
    if count == 0:
        seed_students = [
            (
                'STU-101', 'Rahul Sharma', 'rahul.sharma@example.edu', '+91 98765 43210',
                'BCA', 'Semester 4', 'Active', 3.82, '2024-08-15', '2003-04-12',
                '14 Connaught Place, New Delhi', 'Manoj Sharma', '+91 98765 43219',
                'Passionate about full-stack web development, Python, and cloud services.'
            ),
            (
                'STU-102', 'Ayesha Khan', 'ayesha.khan@example.edu', '+91 98123 45678',
                'BSc IT', 'Semester 6', 'Active', 3.91, '2023-08-10', '2002-11-20',
                '52 Marine Drive, Mumbai', 'Tariq Khan', '+91 98123 45670',
                'Specializing in cloud infrastructure, containerization, and network security.'
            ),
            (
                'STU-103', 'Arjun Mehta', 'arjun.mehta@example.edu', '+91 98345 67890',
                'B.Tech CS', 'Semester 2', 'Active', 3.65, '2025-01-12', '2004-07-08',
                '88 Indiranagar, Bengaluru', 'Suresh Mehta', '+91 98345 67899',
                'AI enthusiast and competitive programmer with strong algorithms background.'
            ),
            (
                'STU-104', 'Sneha Patel', 'sneha.patel@example.edu', '+91 98456 78901',
                'Data Science', 'Semester 4', 'Active', 3.88, '2024-08-15', '2003-09-15',
                '23 Navrangpura, Ahmedabad', 'Kirit Patel', '+91 98456 78900',
                'Focusing on statistical modeling, machine learning, and predictive analytics.'
            ),
            (
                'STU-105', 'Vikram Aditya', 'vikram.aditya@example.edu', '+91 98567 89012',
                'Cybersecurity', 'Semester 6', 'Active', 3.74, '2023-08-10', '2002-03-25',
                '104 Banjara Hills, Hyderabad', 'Ravi Aditya', '+91 98567 89010',
                'Certified ethical hacker focusing on threat detection and cryptography.'
            ),
            (
                'STU-106', 'Priya Nair', 'priya.nair@example.edu', '+91 98678 90123',
                'MCA', 'Semester 2', 'Active', 3.95, '2025-01-12', '2001-12-05',
                '77 Panampilly Nagar, Kochi', 'Mohan Nair', '+91 98678 90120',
                'Dean’s Honor List awardee exploring distributed systems and scalable backends.'
            ),
            (
                'STU-107', 'Devansh Roy', 'devansh.roy@example.edu', '+91 98789 01234',
                'BCA', 'Semester 6', 'Graduated', 3.52, '2023-01-10', '2002-06-18',
                '31 Salt Lake Sector V, Kolkata', 'Subhash Roy', '+91 98789 01230',
                'Graduated with honors, working on open-source educational management tools.'
            ),
            (
                'STU-108', 'Tanya Verma', 'tanya.verma@example.edu', '+91 98890 12345',
                'B.Tech CS', 'Semester 4', 'On Leave', 3.40, '2024-08-15', '2003-02-14',
                '19 Koregaon Park, Pune', 'Alok Verma', '+91 98890 12340',
                'Currently undertaking an accredited industrial internship in systems engineering.'
            )
        ]
        
        cursor.executemany('''
            INSERT INTO students (
                student_code, name, email, phone, course, semester,
                status, gpa, enrollment_date, dob, address,
                guardian_name, guardian_phone, bio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', seed_students)
        conn.commit()

    conn.close()

# Initialize DB on start
init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total students
    cursor.execute('SELECT COUNT(*) FROM students')
    total_students = cursor.fetchone()[0]
    
    # Active students
    cursor.execute("SELECT COUNT(*) FROM students WHERE status = 'Active'")
    active_students = cursor.fetchone()[0]
    
    # Distinct courses count
    cursor.execute('SELECT COUNT(DISTINCT course) FROM students')
    total_courses = cursor.fetchone()[0]
    
    # Average GPA
    cursor.execute('SELECT AVG(gpa) FROM students')
    avg_gpa_val = cursor.fetchone()[0]
    avg_gpa = round(avg_gpa_val, 2) if avg_gpa_val else 0.0
    
    # Recent 5 students
    cursor.execute('SELECT * FROM students ORDER BY id DESC LIMIT 5')
    recent_students = cursor.fetchall()
    
    # Course distribution for dashboard
    cursor.execute('SELECT course, COUNT(*) as count FROM students GROUP BY course ORDER BY count DESC')
    course_stats = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        'index.html',
        total_students=total_students,
        active_students=active_students,
        total_courses=total_courses,
        avg_gpa=avg_gpa,
        recent_students=recent_students,
        course_stats=course_stats
    )

@app.route('/students')
def students():
    search_query = request.args.get('search', '').strip()
    course_filter = request.args.get('course', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch distinct courses and statuses for filters
    cursor.execute('SELECT DISTINCT course FROM students ORDER BY course ASC')
    courses = [row['course'] for row in cursor.fetchall()]
    
    cursor.execute('SELECT DISTINCT status FROM students ORDER BY status ASC')
    statuses = [row['status'] for row in cursor.fetchall()]
    
    # Build query
    sql = 'SELECT * FROM students WHERE 1=1'
    params = []
    
    if search_query:
        sql += ' AND (name LIKE ? OR student_code LIKE ? OR email LIKE ?)'
        like_term = f'%{search_query}%'
        params.extend([like_term, like_term, like_term])
        
    if course_filter:
        sql += ' AND course = ?'
        params.append(course_filter)
        
    if status_filter:
        sql += ' AND status = ?'
        params.append(status_filter)
        
    sql += ' ORDER BY id DESC'
    cursor.execute(sql, params)
    student_list = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        'students.html',
        students=student_list,
        courses=courses,
        statuses=statuses,
        search_query=search_query,
        selected_course=course_filter,
        selected_status=status_filter,
        total_count=len(student_list)
    )

@app.route('/about')
def about():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM students')
    student_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(DISTINCT course) FROM students')
    course_count = cursor.fetchone()[0]
    conn.close()
    
    return render_template('about.html', student_count=student_count, course_count=course_count)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        course = request.form.get('course', '').strip()
        semester = request.form.get('semester', '').strip()
        status = request.form.get('status', 'Active').strip()
        gpa_str = request.form.get('gpa', '3.5').strip()
        enrollment_date = request.form.get('enrollment_date', '').strip()
        dob = request.form.get('dob', '').strip()
        address = request.form.get('address', '').strip()
        guardian_name = request.form.get('guardian_name', '').strip()
        guardian_phone = request.form.get('guardian_phone', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Validation
        if not name or not email or not course or not semester:
            flash('Please fill in all required fields (Name, Email, Course, Semester).', 'error')
            return render_template('add_student.html', form_data=request.form)
            
        try:
            gpa = float(gpa_str) if gpa_str else 3.5
        except ValueError:
            gpa = 3.5

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check email uniqueness
        cursor.execute('SELECT id FROM students WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            flash('A student with this email address already exists.', 'error')
            return render_template('add_student.html', form_data=request.form)
            
        # Generate custom student code
        cursor.execute('SELECT MAX(id) FROM students')
        max_id = cursor.fetchone()[0] or 100
        student_code = f"STU-{max_id + 1}"
        
        cursor.execute('''
            INSERT INTO students (
                student_code, name, email, phone, course, semester,
                status, gpa, enrollment_date, dob, address,
                guardian_name, guardian_phone, bio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_code, name, email, phone, course, semester,
            status, gpa, enrollment_date, dob, address,
            guardian_name, guardian_phone, bio
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        flash(f'Student {name} ({student_code}) added successfully!', 'success')
        return redirect(url_for('student_details', student_id=new_id))
        
    return render_template('add_student.html', form_data={})

@app.route('/students/<int:student_id>')
def student_details(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    conn.close()
    
    if student is None:
        abort(404)
        
    return render_template('student_details.html', student=student)

@app.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    
    if student is None:
        conn.close()
        abort(404)
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        course = request.form.get('course', '').strip()
        semester = request.form.get('semester', '').strip()
        status = request.form.get('status', 'Active').strip()
        gpa_str = request.form.get('gpa', '3.5').strip()
        enrollment_date = request.form.get('enrollment_date', '').strip()
        dob = request.form.get('dob', '').strip()
        address = request.form.get('address', '').strip()
        guardian_name = request.form.get('guardian_name', '').strip()
        guardian_phone = request.form.get('guardian_phone', '').strip()
        bio = request.form.get('bio', '').strip()
        
        if not name or not email or not course or not semester:
            flash('Please fill in all required fields.', 'error')
            conn.close()
            return render_template('edit_student.html', student=student)
            
        try:
            gpa = float(gpa_str) if gpa_str else 3.5
        except ValueError:
            gpa = 3.5
            
        # Check email uniqueness for other students
        cursor.execute('SELECT id FROM students WHERE email = ? AND id != ?', (email, student_id))
        if cursor.fetchone():
            flash('Another student is already using this email address.', 'error')
            conn.close()
            return render_template('edit_student.html', student=student)
            
        cursor.execute('''
            UPDATE students SET
                name = ?, email = ?, phone = ?, course = ?, semester = ?,
                status = ?, gpa = ?, enrollment_date = ?, dob = ?,
                address = ?, guardian_name = ?, guardian_phone = ?, bio = ?
            WHERE id = ?
        ''', (
            name, email, phone, course, semester,
            status, gpa, enrollment_date, dob,
            address, guardian_name, guardian_phone, bio, student_id
        ))
        conn.commit()
        conn.close()
        
        flash(f'Student {name} updated successfully!', 'success')
        return redirect(url_for('student_details', student_id=student_id))
        
    conn.close()
    return render_template('edit_student.html', student=student)

@app.route('/students/<int:student_id>/delete', methods=['POST'])
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, student_code FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    
    if student:
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
        flash(f"Student {student['name']} ({student['student_code']}) was deleted.", 'info')
    else:
        flash('Student record not found.', 'error')
        
    conn.close()
    return redirect(url_for('students'))

# JSON API endpoints for JavaScript interactivity
@app.route('/api/students')
def api_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, student_code, name, email, phone, course, semester, status, gpa FROM students ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/stats')
def api_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM students')
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM students WHERE status = 'Active'")
    active = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(DISTINCT course) FROM students')
    courses = cursor.fetchone()[0]
    cursor.execute('SELECT AVG(gpa) FROM students')
    avg_gpa = cursor.fetchone()[0]
    conn.close()
    return jsonify({
        'total_students': total,
        'active_students': active,
        'total_courses': courses,
        'avg_gpa': round(avg_gpa, 2) if avg_gpa else 0.0
    })

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)