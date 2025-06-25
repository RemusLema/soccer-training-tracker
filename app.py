import streamlit as st
import pandas as pd
from datetime import date

USE_SHEETS = False  # toggle Google Sheets syncing

if USE_SHEETS:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

# ---------- Data Storage Setup ----------
if USE_SHEETS:
    # Setup creds file path or JSON JSON string via env var
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('Training Tracker').sheet1
    data = pd.DataFrame(sheet.get_all_records())
else:
    try:
        data = pd.read_csv('training_log.csv', parse_dates=['date'])
    except FileNotFoundError:
        data = pd.DataFrame(columns=[
            'date','week','day','session_type','exercise','sets','reps','weight','notes'
        ])

# ---------- Streamlit Layout ----------
st.set_page_config(page_title="Soccer Training Tracker", layout="wide")
st.title("⚽ Soccer Training Tracker")

# Week selector
week = st.sidebar.selectbox("Select Week", [f"Week {i}" for i in range(1,7)])
session_date = st.sidebar.date_input("Session Date", date.today())
session_type = st.sidebar.selectbox("Session Type",
    ["Lower Body", "Upper Body", "Conditioning", "Recovery", "Power/Plyo", "Field Fitness"])
st.sidebar.markdown("---")

# Input table for gym sessions
if session_type in ["Lower Body", "Upper Body", "Power/Plyo"]:
    st.header(f"{session_type} - Log Your Session")
    exercises = st.text_area("List exercises (one per line)", 
        "E.g., Back Squat – 4x6–8")
    notes = st.text_area("Session notes (soreness, fatigue, etc.)")
    if st.button("Save Session"):
        for line in exercises.split("\n"):
            data = data.append({
                'date': session_date, 'week': week, 'day': session_date.strftime("%A"),
                'session_type': session_type, 'exercise': line,
                'sets': '', 'reps': '', 'weight': '', 'notes': notes
            }, ignore_index=True)
        if USE_SHEETS:
            sheet.update([data.columns.values.tolist()] + data.values.tolist())
        else:
            data.to_csv('training_log.csv', index=False)
        st.success("Session saved!")

# Field or Conditioning
elif session_type in ["Conditioning", "Field Fitness"]:
    st.header(f"{session_type} – Log Your Workout")
    duration = st.text_input("Duration (e.g., 20 min, 6x20m sprints)")
    notes = st.text_area("Notes (feelings, fatigue, etc.)")
    if st.button("Save Workout"):
        data = data.append({
            'date': session_date, 'week': week, 'day': session_date.strftime("%A"),
            'session_type': session_type, 'exercise': duration,
            'sets':'','reps':'','weight':'', 'notes': notes
        }, ignore_index=True)
        if USE_SHEETS:
            sheet.update([data.columns.values.tolist()] + data.values.tolist())
        else:
            data.to_csv('training_log.csv', index=False)
        st.success("Workout saved!")

# Recovery
else:
    st.header("Recovery or Mobility Day – Notes")
    notes = st.text_area("Tracking notes for your recovery day")
    if st.button("Save Recovery"):
        data = data.append({
            'date': session_date, 'week': week, 'day': session_date.strftime("%A"),
            'session_type': session_type, 'exercise': '',
            'sets':'','reps':'','weight':'', 'notes': notes
        }, ignore_index=True)
        if USE_SHEETS:
            sheet.update([data.columns.values.tolist()] + data.values.tolist())
        else:
            data.to_csv('training_log.csv', index=False)
        st.success("Recovery logged!")

# ---------- View Logs ----------
st.sidebar.markdown("---")
if st.sidebar.checkbox("Show all logs"):
    st.subheader("Training Log")
    st.dataframe(data.sort_values('date'))
