from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
import pymysql 


app = Flask(__name__, template_folder='templates')
app.secret_key = "your_secret_key"  # Replace with a strong secret key

# ✅ Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mentorstudentportal@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'xigx dqpi fwne slur'    # Replace with your app-specific password

mail = Mail(app) 


# ✅ Database Connection Function
def connect_to_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Sabari@8704",
        database="tamil_db",
    )

@app.route('/')
def homes():
    return render_template('index.html')

# ✅ Login Routes
@app.route('/login')
def home():
    return render_template('/student/login.html')

@app.route('/logins')
def homess():
    return render_template('/teacher/login.html')

@app.route('/loginss')
def homesss():
    return render_template('/admin/login.html')


# ✅ Register Student (Status = Pending)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        father_name = request.form['father_name']
        number = request.form['number']
        password = request.form['password']  # Storing plain password (not recommended)
        department = request.form['department']  # Get department from form


# Validate phone number (must be exactly 10 digits)
        if not number.isdigit() or len(number) != 10:
            flash("Contact number must be exactly 10 digits.", "danger")
            return redirect(url_for('register'))


        db = connect_to_database()
        cursor = db.cursor()

        try:
            query = "INSERT INTO users (username, email, father_name, number, password, department, status) VALUES (%s, %s, %s, %s, %s, %s, 'pending')"
            cursor.execute(query, (username, email, father_name, number, password, department))
            db.commit()
            flash("Registration successful! Waiting for admin approval.", "warning")
            return redirect(url_for('home'))
        except pymysql.err.IntegrityError:
            flash("Username or email already exists. Try again.", "danger")
        finally:
            cursor.close()
            db.close()

    return render_template('/student/register.html')


# ✅ Register Teacher (Status = Pending)
@app.route('/registers', methods=['GET', 'POST'])
def registers():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        number = request.form['number']
        password = request.form['password']

        db = connect_to_database()
        cursor = db.cursor()

        try:
            query = "INSERT INTO teacher (username, email, number, password, status) VALUES (%s, %s, %s, %s, 'pending')"
            cursor.execute(query, (username, email, number, password))
            db.commit()
            flash("Teacher registered successfully! Waiting for admin approval.", "warning")
            return redirect(url_for('homess'))
        except pymysql.err.IntegrityError:
            flash("Username already exists. Try again.", "danger")
        finally:
            cursor.close()
            db.close()

    return render_template('/teacher/register.html')



# ✅ Register Admin
@app.route('/registerss', methods=['GET', 'POST'])
def registerss():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        number = request.form['number']
        password = request.form['password']

        db = connect_to_database()
        cursor = db.cursor()

        try:
            query = "INSERT INTO admin (username, email, number, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (username, email, number, password))
            db.commit()
            flash("Admin registered successfully!", "success")
            return redirect(url_for('homesss'))  # Redirect to admin login
        except pymysql.err.IntegrityError as e:
            flash("Username or email already exists. Try again.", "danger")
            print("Database Error:", e)  # Print error for debugging
        except Exception as e:
            flash("Something went wrong!", "danger")
            print("Error:", e)  # Print error for debugging
        finally:
            cursor.close()
            db.close()

    return render_template('/admin/register.html')



# ✅ Student Login (Only Approved Users)
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    db = connect_to_database()
    cursor = db.cursor()

    query = "SELECT id FROM users WHERE username = %s AND password = %s AND status='approved'"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    cursor.close()
    db.close()

    if user:
        session['username'] = username
        session['student_id'] = user[0]  # ✅ Store student_id in session
        flash("Login successful!", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid username/password or waiting for admin approval.", "danger")
        return redirect(url_for('home'))


# ✅ Teacher Login (Only Approved Users)
@app.route('/logins', methods=['POST'])
def logins():
    username = request.form['username']
    password = request.form['password']

    db = connect_to_database()
    cursor = db.cursor()

    query = "SELECT * FROM teacher WHERE username = %s AND password = %s AND status='approved'"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    print("Login Query Result:", user)  # Debugging

    cursor.close()
    db.close()

    if user:
        session['username'] = username
        flash("Login successful!", "success")
        return redirect(url_for('teacher_dashboard'))  # ✅ Fix this
    else:
        flash("Invalid username/password or waiting for admin approval.", "danger")
        return redirect(url_for('homess'))  # ✅ Ensure this points to teacher login

    

@app.route('/loginss', methods=['GET', 'POST'])
def loginss():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = connect_to_database()
        cursor = db.cursor()

        query = "SELECT * FROM admin WHERE username = %s AND password = %s  AND status='approved'"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            session['username'] = username
            flash("Admin login successful!", "success")
            return redirect(url_for('dashboardss'))  # Redirect to admin dashboard
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for('homesss'))  # Redirect back to login page

    return render_template('/admin/login.html')  # Render login page if GET request



# ✅ Admin Dashboard Page
@app.route('/dashboardss')
def dashboardss():
    if 'username' in session:
        return render_template('admin/dashboard.html', username=session['username'])
    else:
        return redirect(url_for('homesss'))


# Dashboard Data API
@app.route('/admin_dashboard_data')
def admin_dashboard_data():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    db = connect_to_database()
    cursor = db.cursor()

    cursor.execute("SELECT id, username, email, role FROM users  WHERE status='approved'")
    approved_users = [dict(zip(['id', 'username', 'email', 'role'], row)) for row in cursor.fetchall()]

    cursor.execute("SELECT id, username, email FROM users WHERE status='pending'")
    students = [dict(zip(['id', 'username', 'email'], row)) for row in cursor.fetchall()]

    cursor.execute("SELECT id, username, email FROM teacher WHERE status='pending'")
    teachers = [dict(zip(['id', 'username', 'email'], row)) for row in cursor.fetchall()]



    # ✅ Add debug prints here
    print("Approved users:", approved_users)
    print("Pending students:", students)
    print("Pending teachers:", teachers)



    cursor.close()
    db.close()

    return jsonify({
        "approved_users": approved_users,
        "students": students,
        "teachers": teachers
    })


# ✅ Send Email on Approval
def send_approval_email(to_email, username):
    msg = Message(
        subject="Account Approved ✅",
        sender=app.config['MAIL_USERNAME'],
        recipients=[to_email]
    )
    
    msg.body = f"Hello {username},\n\nYour account has been approved. You can now log in and access your dashboard.\n\nThanks,\nAdmin"
    mail.send(msg)



@app.route('/admin/approve/<string:user_type>/<int:user_id>', methods=['POST'])
def approve_user(user_type, user_id):
    print(f"Received approve request for {user_type} with ID {user_id}")  # Debug

    db = connect_to_database()
    cursor = db.cursor()

    try:
        if user_type == 'student':
            cursor.execute("UPDATE users SET status = 'approved' WHERE id = %s", (user_id,))
            cursor.execute("SELECT email, username FROM users WHERE id = %s", (user_id,))
        elif user_type == 'teacher':
            cursor.execute("UPDATE teacher SET status = 'approved' WHERE id = %s", (user_id,))
            cursor.execute("SELECT email, username FROM teacher WHERE id = %s", (user_id,))
        else:
            return jsonify({"error": "Invalid user type"}), 400

        user = cursor.fetchone()
        print("Fetched user:", user)  # Debug

        if user:
            email, username = user
            send_approval_email(email, username)

        db.commit()
        print("User approved and email sent.")
        return jsonify({"message": f"{user_type.capitalize()} approved and email sent."})

    except Exception as e:
        db.rollback()
        print("Error approving user:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()

# Delete User
@app.route('/admin/delete/<string:user_type>/<int:user_id>', methods=['POST'])
def delete_user(user_type, user_id):
    db = connect_to_database()
    cursor = db.cursor()

    if user_type == 'student':
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    elif user_type == 'teacher':
        cursor.execute("DELETE FROM teacher WHERE id = %s", (user_id,))
    else:
        return jsonify({"error": "Invalid user type"}), 400

    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": f"{user_type.capitalize()} deleted."})



# ✅ Dashboards
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        db = connect_to_database()
        cursor = db.cursor()

        # ✅ Fetch student ID from the database based on username
        cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
        student = cursor.fetchone()
        cursor.close()
        db.close()

        if student:
            student_id = student[0]  # Get student ID from the result
            return render_template('/student/dashboard.html', username=session['username'], student_id=student_id)
        else:
            flash("Student data not found.", "danger")
            return redirect(url_for('home'))

    else:
        flash("Please log in first.", "warning")
        return redirect(url_for('home'))


# ✅ Teacher Dashboard (Show Marks)
@app.route('/dashboardsss')
def teacher_dashboard():
    if 'username' not in session:
        return redirect(url_for('homess'))

    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM marks")
    marks = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('/teacher/dashboard.html', username=session['username'], marks=marks)

# ✅ Convert Marks to Grades
def convert_to_grade(marks):
    marks = int(marks)
    if marks >= 90:
        return "S"  # Outstanding
    elif marks >= 80:
        return "A"  # Excellent
    elif marks >= 70:
        return "B"  # Good
    elif marks >= 60:
        return "C"  # Average
    elif marks >= 50:
        return "D"  # Below Average
    else:
        return "U"  # Arrear
 

@app.route("/check_duplicate/<student_id>/<subject>", methods=["GET"])
def check_duplicate(student_id, subject):
    conn = connect_to_database()  # ✅ Use the correct function name
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM marks WHERE student_id = %s AND subject = %s", (student_id, subject))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify({"exists": bool(result)})


# ✅ Get Subject-Wise Marks and Grades
@app.route('/get_subject_marks/<subject>', methods=['GET'])
def get_subject_marks(subject):
    db = connect_to_database()
    if db is None:
        return jsonify({"success": False, "message": "Database connection failed!"})

    cursor = db.cursor()
        
    # ✅ Make sure to select 'id' from the database
    query = "SELECT id, student_id, student_name, marks FROM marks WHERE subject = %s"

    try:
        cursor.execute(query, (subject,))
        results = cursor.fetchall()
    except Exception as e:
        return jsonify({"success": False, "message": f"Query execution failed: {str(e)}"})
    finally:
        cursor.close()
        db.close()

    marks_list = []
    for row in results:
        mark_id, student_id, student_name, marks = row  # ✅ Update unpacking to match query
        grade = convert_to_grade(marks)
        marks_list.append({
            'id': mark_id,  # ✅ Include 'id' for delete functionality
            'student_id': student_id,
            'student_name': student_name,
            'marks': marks,
            'grade': grade
        })

    return jsonify(marks_list)


@app.route('/upload_marks', methods=['POST'])
def upload_marks():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized Access"})

    data = request.get_json()
    required_fields = ["studentId", "studentName", "subject", "marks"]
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"success": False, "message": "Missing required fields!"})

    studentId = data['studentId']
    studentName = data['studentName']
    subject = data['subject']
    marks = data['marks']

    try:
        marks = int(marks)
        grade = convert_to_grade(marks)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid marks value!"})  # ✅ Prevents non-numeric errors

    db = connect_to_database()
    if db is None:
        return jsonify({"success": False, "message": "Database connection failed!"})

    cursor = db.cursor()

    try:
        # ✅ Check if student exists and is approved
        cursor.execute("SELECT id FROM users WHERE id = %s AND status = 'approved'", (studentId,))
        student = cursor.fetchone()

        if not student:
            return jsonify({"success": False, "message": "Invalid or unapproved student!"})  # ✅ Prevents unauthorized uploads

        # ✅ Insert marks only if the student is approved
        query = "INSERT INTO marks (student_id, student_name, subject, marks, grade) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (studentId, studentName, subject, marks, grade))
        db.commit()

        return jsonify({"success": True, "message": "Marks uploaded successfully!"})

    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": f"Error inserting marks: {str(e)}"})  # ✅ More detailed error messages

    finally:
        cursor.close()
        db.close()


# ✅ Delete Marks
@app.route('/delete_marks/<int:mark_id>', methods=['DELETE'])
def delete_marks(mark_id):
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized Access"})

    db = connect_to_database()
    if db is None:
        return jsonify({"success": False, "message": "Database connection failed!"})

    cursor = db.cursor()
    query = "DELETE FROM marks WHERE id = %s"
    
    cursor.execute(query, (mark_id,))
    db.commit()

    if cursor.rowcount == 0:
        return jsonify({"success": False, "message": "No record found with this ID"})  # ✅ Proper handling if mark ID doesn't exist

    cursor.close()
    db.close()

    return jsonify({"success": True, "message": "Marks deleted successfully!"})


@app.route('/get_student_marks/<student_id>')
def get_student_marks(student_id):
    db = connect_to_database()
    cursor = db.cursor()

    cursor.execute("SELECT subject, marks, grade FROM marks WHERE student_id = %s", (student_id,))
    results = cursor.fetchall()

    cursor.close()
    db.close()

    if not results:
        return jsonify({"success": False, "message": "No results found for this student."})  # ✅ Debugging message

    marks_list = [{"subject": row[0], "marks": row[1], "grade": row[2]} for row in results]
    return jsonify(marks_list)

@app.route("/get_approved_students")
def get_approved_students():
    db = connect_to_database()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT id, username, email FROM users WHERE status = 'approved'")
        students = cursor.fetchall()

        student_list = [
            {"id": student[0], "username": student[1], "email": student[2]}
            for student in students
        ]

        return jsonify(student_list)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        cursor.close()
        db.close()

@app.route('/get_student_details/<int:student_id>', methods=['GET'])
def get_student_details(student_id):
    db = connect_to_database()
    if db is None:
        return jsonify({"success": False, "message": "Database connection failed!"})

    cursor = db.cursor(pymysql.cursors.DictCursor)  # ✅ Use dictionary cursor

    try:
        # Fetch both username and department
        query = "SELECT username, department FROM users WHERE id = %s AND status = 'approved'"
        cursor.execute(query, (student_id,))
        student = cursor.fetchone()

        if student:
            return jsonify({"success": True, "studentName": student["username"], "department": student["department"]})
        else:
            return jsonify({"success": False, "message": "Student not found or not approved"})

    except Exception as e:
        print(f"Error fetching student details: {e}")  # ✅ Debugging output
        return jsonify({"success": False, "message": "An error occurred while fetching data"})

    finally:
        cursor.close()
        db.close()


@app.route("/post_announcement", methods=["POST"])
def post_announcement():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"success": False, "message": "Title and content are required."})

    try:
        # ✅ Reuse your existing function
        conn = connect_to_database()
        cur = conn.cursor()

        # ✅ Insert the announcement
        cur.execute("INSERT INTO announcements (title, content) VALUES (%s, %s)", (title, content))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"success": True, "message": "Announcement posted successfully."})
    
    except Exception as e:
        print("Error posting announcement:", e)
        return jsonify({"success": False, "message": "Server error."})




@app.route("/get_announcements", methods=["GET"])
def get_announcements():
    try:
        conn = connect_to_database()
        cur = conn.cursor()
        cur.execute("SELECT title, content, timestamp FROM announcements ORDER BY timestamp DESC")
        rows = cur.fetchall()

        # Format timestamp properly if needed
        formatted_rows = []
        for row in rows:
            formatted_rows.append({
                "title": row[0],
                "content": row[1],
                "timestamp": row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else None
            })

        cur.close()
        conn.close()
        return jsonify(formatted_rows)
    except Exception as e:
        print("Error fetching announcements:", e)
        return jsonify([])

@app.route("/get_student_announcements", methods=["GET"])
def get_student_announcements():
    try:
        conn = connect_to_database()  # Use your database connection function
        cur = conn.cursor()
        cur.execute("SELECT title, content, timestamp FROM announcements ORDER BY timestamp DESC")
        rows = cur.fetchall()

        # Format timestamp properly if needed
        formatted_rows = []
        for row in rows:
            formatted_rows.append({
                "title": row[0],
                "content": row[1],
                "timestamp": row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else None
            })

        cur.close()
        conn.close()
        return jsonify(formatted_rows)
    except Exception as e:
        print("Error fetching announcements:", e)
        return jsonify([])  # Return an empty list if there's an error


# ✅ Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('homes'))

if __name__ == "__main__":
    app.run(debug=True)
