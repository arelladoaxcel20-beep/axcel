import os
import io
import csv
from flask import Flask, request, render_template_string, redirect, url_for, Response
import psycopg2
import psycopg2.extras
from database import get_db_connection, init_db

app = Flask(__name__)

# --- Enhanced Helper Logic ---
PASSING_GRADE = 75

def get_student_status(grade):
    if grade >= 90: return {"label": "Exemplary", "color": "emerald"}
    if grade >= 75: return {"label": "Stable", "color": "blue"}
    return {"label": "At Risk", "color": "rose"}

def get_letter_grade(grade):
    if grade >= 90: return "A"
    elif grade >= 80: return "B"
    elif grade >= 75: return "C"
    else: return "F"

# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('list_students'))

@app.route('/students')
def list_students():
    conn = get_db_connection()
    if not conn:
        return "Database connection error.", 500
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    # Statistics Calculations
    total = len(students)
    at_risk = sum(1 for s in students if s['grade'] < PASSING_GRADE)
    avg_grade = sum(s['grade'] for s in students) / total if total else 0
    
    # Grade Distribution
    grade_dist = {"A": 0, "B": 0, "C": 0, "F": 0}
    for s in students:
        grade_dist[get_letter_grade(s['grade'])] += 1

    # Tailwind-based Modern Dashboard Template
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>VISTA | Analytics Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
            .glass-card { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(226, 232, 240, 0.8); }
        </style>
    </head>
    <body class="p-6">
        <div class="max-w-7xl mx-auto">
            <header class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                <div>
                    <h1 class="text-3xl font-bold text-slate-900">Academic Intelligence</h1>
                    <p class="text-slate-500">Monitoring performance across {{ total_students }} active students</p>
                </div>
                <div class="flex gap-3">
                    <a href="/export_csv" class="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition shadow-sm">Export Data</a>
                    <a href="/add_student_form" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition shadow-sm shadow-indigo-200">+ New Entry</a>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="glass-card p-6 rounded-2xl shadow-sm">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Class Average</p>
                    <h2 class="text-3xl font-bold text-slate-800 mt-1">{{ avg_grade|round(1) }}%</h2>
                    <div class="mt-2 text-xs text-indigo-600 font-medium">Global Benchmarking</div>
                </div>
                <div class="glass-card p-6 rounded-2xl shadow-sm">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">At Risk Status</p>
                    <h2 class="text-3xl font-bold text-rose-600 mt-1">{{ at_risk }}</h2>
                    <div class="mt-2 text-xs text-slate-500">Requires immediate triage</div>
                </div>
                <div class="glass-card p-6 rounded-2xl shadow-sm">
                    <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Pass Rate</p>
                    <h2 class="text-3xl font-bold text-emerald-600 mt-1">{{ ((total_students - at_risk) / total_students * 100)|round(1) if total_students else 0 }}%</h2>
                    <div class="mt-2 text-xs text-slate-500">Of total population</div>
                </div>
                <div class="glass-card p-6 rounded-2xl shadow-sm bg-indigo-900">
                    <p class="text-xs font-semibold text-indigo-300 uppercase tracking-wider">System Health</p>
                    <h2 class="text-3xl font-bold text-white mt-1">Optimal</h2>
                    <div class="mt-2 text-xs text-indigo-400">Database connected</div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div class="lg:col-span-2">
                    <div class="glass-card rounded-2xl shadow-sm overflow-hidden">
                        <div class="p-6 border-b border-slate-100 flex justify-between items-center">
                            <h3 class="font-bold text-slate-800">Student Intelligence Roster</h3>
                            <input type="text" id="search" placeholder="Filter by name..." class="bg-slate-50 border-0 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 w-48">
                        </div>
                        <table class="w-full text-left">
                            <thead class="bg-slate-50 text-slate-500 text-xs uppercase font-bold">
                                <tr>
                                    <th class="px-6 py-4">Student</th>
                                    <th class="px-6 py-4">Metrics</th>
                                    <th class="px-6 py-4">Status</th>
                                    <th class="px-6 py-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="student-rows" class="divide-y divide-slate-100 text-sm">
                                {% for s in students %}
                                {% set status = get_student_status(s.grade) %}
                                <tr class="hover:bg-slate-50/50 transition">
                                    <td class="px-6 py-4">
                                        <div class="font-semibold text-slate-800">{{ s.name }}</div>
                                        <div class="text-xs text-slate-400">Section {{ s.section }}</div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <div class="flex items-center gap-2">
                                            <span class="text-slate-700 font-medium">{{ s.grade }}%</span>
                                            <div class="w-16 bg-slate-100 h-1.5 rounded-full overflow-hidden">
                                                <div class="bg-indigo-500 h-full" style="width: {{ s.grade }}%"></div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <span class="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-{{ status.color }}-100 text-{{ status.color }}-700">
                                            {{ status.label }}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 text-right">
                                        <div class="flex justify-end gap-2">
                                            <a href="/edit_student/{{s.id}}" class="p-1.5 text-slate-400 hover:text-indigo-600 transition">Edit</a>
                                            <form action="/delete_student/{{s.id}}" method="POST" onsubmit="return confirm('Archive record?')">
                                                <button type="submit" class="p-1.5 text-slate-400 hover:text-rose-600 transition">Delete</button>
                                            </form>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="space-y-6">
                    <div class="glass-card p-6 rounded-2xl shadow-sm">
                        <h3 class="font-bold text-slate-800 mb-6">Grade Distribution</h3>
                        <canvas id="gradeChart" height="250"></canvas>
                        <div class="mt-6 space-y-3">
                            {% for grade, count in grade_dist.items() %}
                            <div class="flex justify-between items-center text-sm">
                                <span class="text-slate-500">Grade {{ grade }}</span>
                                <span class="font-bold text-slate-800">{{ count }} Students</span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="bg-indigo-600 p-6 rounded-2xl shadow-lg text-white">
                        <h4 class="font-bold mb-2">Pro Tip</h4>
                        <p class="text-sm text-indigo-100 opacity-80">Students flagged as "At Risk" should be prioritized for the upcoming peer-tutoring sessions.</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Search Filtering
            document.getElementById('search').addEventListener('input', function(e) {
                const term = e.target.value.toLowerCase();
                document.querySelectorAll('#student-rows tr').forEach(row => {
                    row.style.display = row.innerText.toLowerCase().includes(term) ? '' : 'none';
                });
            });

            // Chart Logic
            const ctx = document.getElementById('gradeChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['A', 'B', 'C', 'F'],
                    datasets: [{
                        data: [{{grade_dist['A']}}, {{grade_dist['B']}}, {{grade_dist['C']}}, {{grade_dist['F']}}],
                        backgroundColor: ['#6366f1', '#38bdf8', '#fbbf24', '#f43f5e'],
                        borderWidth: 0,
                        hoverOffset: 10
                    }]
                },
                options: {
                    cutout: '70%',
                    plugins: { legend: { display: false } }
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html, 
                                 students=students, 
                                 total_students=total, 
                                 at_risk=at_risk, 
                                 avg_grade=avg_grade, 
                                 grade_dist=grade_dist, 
                                 get_student_status=get_student_status)

# Keep other routes (add_student, edit_student, export_csv) the same but update their HTML templates to use Tailwind!

if __name__ == '__main__':
    init_db() 
    app.run(debug=True)
