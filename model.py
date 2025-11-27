import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
import os

DATA = "students.csv"
MODEL = "model.pkl"

if not os.path.exists(DATA):
    raise FileNotFoundError("students.csv not found. Create it with proper columns.")
data = pd.read_csv(DATA)
data.columns = data.columns.str.strip()

required = ['Hours_Studied','Sleep_Hours','Attendance','Marks']
for col in required:
    if col not in data.columns:
        raise ValueError(f"Missing required column: {col}")

X = data[['Hours_Studied','Sleep_Hours','Attendance']]
y = data['Marks']

model = LinearRegression()
model.fit(X, y)

pickle.dump(model, open(MODEL, "wb"))
print("Model trained and saved to", MODEL)


# # model.py
# import pandas as pd
# from sklearn.linear_model import LinearRegression
# import pickle

# df = pd.read_csv("students.csv")  # must contain: Hours_Studied, Sleep_Hours, Attendance, Marks

# X = df[['Hours_Studied', 'Sleep_Hours', 'Attendance']]
# y = df['Marks']
# model = LinearRegression()
# model.fit(X, y)

# pickle.dump(model, open("model.pkl", "wb"))
# print("model.pkl created successfully!")
