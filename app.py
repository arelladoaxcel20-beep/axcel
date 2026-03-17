from flask import Flask, jsonify, request, render_template_string, redirect, url_for

app = Flask(__name__)

# --- In-Memory Database ---
# Using a list of dictionaries to simulate a database
students = [
    {"id": 1, "name": "Juan Dela Cruz", "grade": 85, "section": "Stallman"},
    {"id": 2, "name": "Maria Clara", "grade": 90, "section": "Stallman"},
    {"id": 3, "name": "Pedro Penduko", "grade": 72, "section": "Zion"}
]

# --- UI Components (Shared Layout) ---
HEADER = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Management System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-4xl mx-auto">
"""
FOOTER = "</div></body></html>"

# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('list_students'))

# 1. VIEW ALL STUDENTS
@app.route('/students')
def list_students():
    html = HEADER + """
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">Student Roster</h2>
        <a href="/add_student_form" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">+ Add Student</a>
    </div>
    
    <div class="bg-white shadow-sm rounded-xl overflow-hidden border border-gray-200">
        <table class="w-full text-left">
            <thead class="bg-gray-50 border-b border-gray-200 text-gray-600 text-sm uppercase">
                <tr>
                    <th class="px-6 py-4">ID</th>
                    <th class="px-6 py-4">Name</th>
                    <th class="px-6 py-4">Grade</th>
                    <th class="px-6 py-4">Section</th>
                    <th class="px-6 py-4 text-right">Actions</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                {% for s in students %}
                <tr class="hover:bg-gray-50 transition">
                    <td class="px-6 py-4 font-mono text-gray-400">#{{s.id}}</td>
                    <td class="px-6 py-4 font-semibold text-gray-800">{{s.name}}</td>
                    <td class="px-6 py-4">
                        <span class="px-2 py-1 rounded text-xs font-bold {{ 'bg-green-100 text-green-700' if s.grade >= 75 else 'bg-red-100 text-red-700' }}">
                            {{s.grade}}%
                        </span>
                    </td>
                    <td class="px-6 py-4 text-gray-500">{{s.section}}</td>
                    <td class="px-6 py-4 text-right">
                        <a href="/edit_student/{{s.id}}" class="text-blue-600 hover:underline mr-3">Edit</a>
                        <a href="/delete_student/{{s.id}}" class="text-red-500 hover:underline" onclick="return confirm('Delete this student?')">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    """ + FOOTER
    return render_template_string(html, students=students)

# 2. ADD STUDENT (Form & Logic)
@app.route('/add_student_form')
def add_student_form():
    html = HEADER + """
    <div class="bg-white p-8 rounded-xl shadow-sm border border-gray-200 max-w-md mx-auto">
        <h2 class="text-xl font-bold mb-6 text-gray-800">Add New Student</h2>
        <form action="/add_student" method="POST" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700">Full Name</label>
                <input type="text" name="name" class="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none" required>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Grade (0-100)</label>
                <input type="number" name="grade" class="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none" min="0" max="100" required>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Section</label>
                <input type="text" name="section" class="w-full mt-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none" required>
            </div>
            <div class="pt-4 flex justify-between">
                <a href="/students" class="text-gray-500 hover:underline py-2">Cancel</a>
                <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition">Save Student</button>
            </div>
        </form>
    </div>
    """ + FOOTER
