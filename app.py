import os
from flask import Flask, request, render_template_string, redirect, url_for
import psycopg2
import psycopg2.extras

# Import your database connection logic!
from database import get_db_connection, init_db

app = Flask(__name__)

# Force Render to initialize the table when the app boots up
init_db()

# --- UI Layout Helper ---
LAYOUT_START = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Analytics Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f3f4f6; }</style>
</head>
<body class="p-4 md:p-10 text-slate-800">
    <div class="max-w-5xl mx-auto">
"""
LAYOUT_END = "</div></body></html>"

# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('list_students'))

@app.route('/students')
def list_students():
    # 1. Fetch live data from PostgreSQL
    conn = get_db_connection()
    if not conn:
        return "Database connection error.", 500
        
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM students ORDER BY id ASC")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    # --- Logic: Calculate Real-time Insights ---
    total = len(students)
    avg = sum(s['grade'] for s in students) / total if total else 0
    passing = sum(1 for s in students if s['grade'] >= 75)
    pass_rate = (passing / total * 100) if total else 0
    top_student = max(students, key=lambda x: x['grade'])['name'] if students else "N/A"

    html = LAYOUT_START + """
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
            <div>
                <h1 class="text-3xl font-extrabold tracking-tight">Student Analytics</h1>
                <p class="text-slate-500">Managing {{total}} active records</p>
            </div>
            <div class="flex gap-2">
                <a href="/add_student_form" class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-semibold shadow-sm transition-all">+ Add New Student</a>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Class Average</p>
                <h2 class="text-3xl font-bold mt-1 text-indigo-600">{{avg|round(1)}}%</h2>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Pass Rate</p>
                <h2 class="text-3xl font-bold mt-1 text-emerald-500">{{pass_rate|round(1)}}%</h2>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">Top Performer</p>
                <h2 class="text-3xl font-bold mt-1 text-slate-800 truncate">{{top_student}}</h2>
            </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div class="p-6 border-b border-slate-100 bg-slate-50/50 flex flex-col md:flex-row justify-between gap-4">
                <h3 class="font-bold text-lg">Student Roster</h3>
                <input type="text" id="tableSearch" placeholder="Search by name or section..." 
                       class="px-4 py-2 border border-slate-200 rounded-lg text-sm w-full md:w-64 focus:ring-2 focus:ring-indigo-500 outline-none">
            </div>
            
            <table class="w-full text-left border-collapse">
                <thead class="text-xs font-bold text-slate-500 uppercase bg-slate-50/50">
                    <tr>
                        <th class="px-6 py-4">Student Name</th>
                        <th class="px-6 py-4">Section</th>
                        <th class="px-6 py-4 text-center">Grade</th>
                        <th class="px-6 py-4 text-center">Status</th>
                        <th class="px-6 py-4 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody id="studentTable" class="divide-y divide-slate-100">
                    {% for s in students %}
                    <tr class="hover:bg-slate-50 transition-colors">
                        <td class="px-6 py-4 font-semibold text-slate-700">{{s.name}}</td>
                        <td class="px-6 py-4 text-slate-500">{{s.section}}</td>
                        <td class="px-6 py-4 text-center font-mono font-bold">{{s.grade}}%</td>
                        <td class="px-6 py-4 text-center">
                            {% if s.grade >= 75 %}
                            <span class="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold">PASSING</span>
                            {% else %}
                            <span class="bg-rose-100 text-rose-700 px-3 py-1 rounded-full text-xs font-bold">AT RISK</span>
                            {% endif %}
                        </td>
                        <td class="px-6 py-4 text-right">
                            <div class="flex justify-end gap-3 text-sm">
                                <a href="/edit_student/{{s.id}}" class="text-indigo-600 hover:text-indigo-800 font-medium">Edit</a>
                                <a href="/delete_student/{{s.id}}" onclick="return confirm('Delete record?')" class="text-slate-400 hover:text-rose-600">Delete</a>
                            </div>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="5" class="px-6 py-8 text-center text-slate-500">No students found. Add one above!</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <script>
            // Client-side Search Logic
            document.getElementById('tableSearch').addEventListener('keyup', function() {
                const term = this.value.toLowerCase();
                const rows = document.querySelectorAll('#studentTable tr');
                rows.forEach(row => {
                    // Skip the "No students found" row if it exists
                    if(row.children.length === 1) return; 
                    
                    const text = row.innerText.toLowerCase();
                    row.style.display = text.includes(term) ? '' : 'none';
                });
            });
        </script>
    """ + LAYOUT_END
    return render_template_string(html, students=students, total=total, avg=avg, pass_rate=pass_rate, top_student=top_student)

@app.route('/add_student_form')
def add_student_form():
    html = LAYOUT_START + """
    <div class="max-w-md mx-auto bg-white p-8 rounded-3xl shadow-sm border border-slate-200 mt-10">
        <h2 class="text-2xl font-bold mb-2">New Enrollment</h2>
        <p class="text-slate-500 mb-6 text-sm">Fill in the student details below.</p>
        <form action="/add_student" method="POST" class="space-y-4">
            <div>
                <label class="block text-xs font-bold text-slate-400 uppercase mb-1">Full Name</label>
                <input type="text" name="name" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none" placeholder="e.g. John Doe" required autofocus>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-bold text-slate-400 uppercase mb-1">Grade</label>
                    <input type="number" name="grade" min="0" max="100" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none" placeholder="0-100" required>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-400 uppercase mb-1">Section</label>
                    <input type="text" name="section" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none" placeholder="Section Name" required>
                </div>
            </div>
            <div class="pt-6 flex flex-col gap-3">
                <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-xl font-bold shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition">Save Student</button>
                <a href="/students" class="text-center text-slate-400 text-sm hover:text-slate-600">Cancel and Return</a>
            </div>
        </form>
    </div>
    """ + LAYOUT_END
    return render_template_string(html)

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form.get("name")
    grade = int(request.form.get("grade", 0))
    section = request.form.get("section")
    
    # 2. INSERT into PostgreSQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, grade, section) VALUES (%s, %s, %s)", (name, grade, section))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('list_students'))

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if request.method == 'POST':
        name = request.form["name"]
        grade = int(request.form["grade"])
        section = request.form["section"]
        
        # 3. UPDATE PostgreSQL
        cursor.execute("UPDATE students SET name = %s, grade = %s, section = %s WHERE id = %s", (name, grade, section, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_students'))

    # GET Request: Fetch the specific student to pre-fill the form
    cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if not student: 
        return "Student Not Found", 404

    html = LAYOUT_START + f"""
    <div class="max-w-md mx-auto bg-white p-8 rounded-3xl shadow-sm border border-slate-200 mt-10">
        <h2 class="text-2xl font-bold mb-6 italic text-indigo-600">Updating Record #{id}</h2>
        <form method="POST" class="space-y-4">
            <input type="text" name="name" value="{student['name']}" class="w-full p-3 border border-slate-200 rounded-xl mb-2 focus:ring-2 focus:ring-indigo-500" required>
            <input type="number" name="grade" value="{student['grade']}" class="w-full p-3 border border-slate-200 rounded-xl mb-2 focus:ring-2 focus:ring-indigo-500" required>
            <input type="text" name="section" value="{student['section']}" class="w-full p-3 border border-slate-200 rounded-xl mb-4 focus:ring-2 focus:ring-indigo-500" required>
            <button type="submit" class="w-full bg-emerald-600 text-white py-3 rounded-xl font-bold hover:bg-emerald-700 transition">Update Record</button>
            <a href="/students" class="block text-center text-slate-400 text-sm mt-4">Cancel</a>
        </form>
    </div>
    """ + LAYOUT_END
    return render_template_string(html)

@app.route('/delete_student/<int:id>')
def delete_student(id):
    # 4. DELETE from PostgreSQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('list_students'))

if __name__ == '__main__':
    app.run(debug=True)
