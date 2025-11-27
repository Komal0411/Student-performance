from flask import Flask, render_template, request, send_file, redirect, url_for
import pickle, sqlite3, os, pandas as pd
from datetime import datetime
import base64
import plotly.express as px

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'change-this-secret'

MODEL_PATH = "model.pkl"
DB_PATH = "predictions.db"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("model.pkl not found — run model.py first to create it.")
model = pickle.load(open(MODEL_PATH, "rb"))

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hours REAL,
            sleep REAL,
            attendance REAL,
            marks REAL,
            grade TEXT,
            date_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Utilities
def grade_from_marks(m):
    if m >= 90: return "A+"
    if m >= 80: return "A"
    if m >= 70: return "B"
    if m >= 60: return "C"
    return "D"

def get_suggestions_overall(df):
    suggestions = []
    if df.empty:
        return ["No data available yet — make predictions to generate analysis."]
    avg_hours = df['hours'].mean()
    avg_sleep = df['sleep'].mean()
    avg_att = df['attendance'].mean()
    avg_marks = df['marks'].mean()
    if avg_hours < 4:
        suggestions.append("Average study hours are low — encourage 4+ hours/day.")
    if avg_sleep < 6:
        suggestions.append("Average sleep is under 6 hours — healthy sleep improves learning.")
    if avg_att < 75:
        suggestions.append("Attendance average is low — increase classroom engagement.")
    if avg_marks < 60:
        suggestions.append("Overall marks are low — focus on revision & practice tests.")
    if avg_marks >= 85:
        suggestions.append("Overall performance is good — maintain consistency.")
    return suggestions

def get_suggestions_personal(hours, sleep, attendance, predicted):
    suggestions = []
    if hours < 2:
        suggestions.append("Increase study time to at least 3–4 hours per day.")
    elif hours < 4:
        suggestions.append("Try extending study sessions; break into focused blocks.")
    if sleep < 6:
        suggestions.append("Improve sleep schedule for better memory consolidation.")
    if attendance < 75:
        suggestions.append("Increase attendance and participation in classes.")
    if predicted < 60:
        suggestions.append("Revise core topics, take mock tests, and seek help for weak areas.")
    if predicted >= 85:
        suggestions.append("Excellent — practice advanced problems and maintain routine.")
    return suggestions

# Plotly graphs generator
def generate_plotly_graphs(df):
    graphs = {}
    if df.empty:
        return graphs

    # Trend
    fig_trend = px.line(df, x='date_time', y='marks', title="Trend: Predicted Marks Over Time")
    graphs['trend'] = fig_trend.to_html(full_html=False)

    # Hours vs Marks
    fig_h = px.scatter(df, x='hours', y='marks', size='attendance',
                       color='marks', title="Hours vs Marks (interactive)")
    graphs['hours'] = fig_h.to_html(full_html=False)

    # Sleep vs Marks
    fig_s = px.scatter(df, x='sleep', y='marks', color='sleep', title="Sleep vs Marks")
    graphs['sleep'] = fig_s.to_html(full_html=False)

    # Attendance vs Marks
    fig_a = px.scatter(df, x='attendance', y='marks', color='marks', title="Attendance vs Marks")
    graphs['attendance'] = fig_a.to_html(full_html=False)

    # 3D Plot
    fig3d = px.scatter_3d(df, x='hours', y='sleep', z='marks', color='marks', title='3D: Hours / Sleep / Marks')
    graphs['3d'] = fig3d.to_html(full_html=False)

    # Correlation heatmap (simple)
    corr = df[['hours','sleep','attendance','marks']].corr()
    fig_corr = px.imshow(corr, text_auto=True, title="Correlation Matrix")
    graphs['corr'] = fig_corr.to_html(full_html=False)

    return graphs

# Routes
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        hours = float(request.form.get('hours', 0))
        sleep = float(request.form.get('sleep', 0))
        attendance = float(request.form.get('attendance', 0))

        predicted = float(model.predict([[hours, sleep, attendance]])[0])
        grade = grade_from_marks(predicted)
        personal_suggestions = get_suggestions_personal(hours, sleep, attendance, predicted)

        # save to DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO predictions (hours, sleep, attendance, marks, grade, date_time) VALUES (?, ?, ?, ?, ?, ?)",
                  (hours, sleep, attendance, predicted, grade, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        return render_template("result.html", marks=round(predicted,2), grade=grade,
                               suggestions=personal_suggestions)
    except Exception as e:
        return f"Prediction error: {e}", 500

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    try:
        file = request.files['file']
        df = pd.read_csv(file.stream)
        df.columns = df.columns.str.strip()
        preds = model.predict(df[['Hours_Studied','Sleep_Hours','Attendance']])
        df['Predicted_Marks'] = preds
        out = "output_predictions.csv"
        df.to_csv(out, index=False)
        return send_file(out, as_attachment=True)
    except Exception as e:
        return f"CSV upload error: {e}", 400

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM predictions ORDER BY id DESC", conn)
    conn.close()

    # If you have a separate students.csv dataset and want to show it, you can read it safely:
    # if os.path.exists('students.csv'):
    #     students_df = pd.read_csv('students.csv')
    # else:
    #     students_df = pd.DataFrame()

    graphs = generate_plotly_graphs(df)
    recent = df.head(10).to_dict(orient='records')

    # ER diagram path (the uploaded file)
    er_path = "/mnt/data/A_digital_diagram_in_Entity-Relationship_Diagram_(.png"
    # If you moved the file to static/, use: er_path = url_for('static', filename='er_diagram.png')

    summary = {
        'count': int(df.shape[0]),
        'avg_marks': float(df['marks'].mean()) if not df.empty else None,
        'avg_hours': float(df['hours'].mean()) if not df.empty else None
    }

    return render_template("dashboard.html", graphs=graphs, recent=recent, summary=summary, er_path=er_path)

@app.route('/analysis')
def analysis():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM predictions ORDER BY id ASC", conn)
    conn.close()

    graphs = generate_plotly_graphs(df)
    suggestions = get_suggestions_overall(df)

    # send raw data also for non-plotly fallback
    data_records = df.to_dict(orient='records')
    return render_template("analysis.html", graphs=graphs, suggestions=suggestions, data=data_records)

@app.route('/create_planner', methods=['POST'])
def create_planner():
    subjects = request.form['subjects'].split(',')
    subjects = [s.strip() for s in subjects if s.strip()]
    hours_per_day = float(request.form['hours'])
    if len(subjects) == 0:
        return redirect(url_for('index'))

    per_subject_daily = round(hours_per_day / len(subjects), 2)
    table = []
    for s in subjects:
        table.append({
            'Subject': s,
            'Daily Hours': per_subject_daily,
            'Priority': 'Medium',
            'Recommended Strategy': 'Revise & practice with past papers'
        })
    # save csv for download
    df_plan = pd.DataFrame(table)
    df_plan.to_csv("static/study_plan.csv", index=False)
    return render_template("study_plan.html", table=table)

@app.route('/download_db')
def download_db():
    return send_file(DB_PATH, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
