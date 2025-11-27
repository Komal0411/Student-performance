Student Performance Prediction – ML + Flask Web App

This project predicts student marks & grade based on:
Study Hours
Sleep Hours
Attendance

It also provides:
✔ AI-generated suggestions
✔ Dashboard with analytics
✔ CSV upload & prediction
✔ Study planner generator
✔ SQLite database integration

File structure 

├── app.py               # Flask App
├── model.py             # ML Model Training
├── model.pkl            # Saved ML Model
├── predictions.db       # SQLite database (auto-created)
├── requirements.txt     # Dependencies
├── templates/
│   ├── index.html
│   ├── result.html
│   ├── dashboard.html
│   ├── analysis.html
│   ├── study_plan.html
├── static/
│   ├── style.css
│   ├── main.js
│   ├── study_plan.csv   # Auto Generated
└── README.md            # Documentation

Installation : pip install -r requirements.txt
Train model : py model.py
