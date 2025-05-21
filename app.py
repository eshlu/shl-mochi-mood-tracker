#setup
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
import json

#gsheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# creds_dict = st.secrets["gcp_service_account"]
# creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope) 
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("StephanieLu_Mochi_Moods").sheet1  

#streamlit
st.set_page_config(page_title="Mochi Queue Mood", layout="centered")
st.title("Mochi Mood Logger")

with st.form("mood_form"):
    mood = st.selectbox("Your current ticket queue mood?", ["😠","😐","😊", "🎉"])
    note = st.text_input("Optional note")
    submitted = st.form_submit_button("Log Mood")

    if submitted:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, mood, note])
        st.success("Mood logged!")

#viz
#TODO: add user-filtering
df = pd.DataFrame(sheet.get_all_records())

if not df.empty:
    today = datetime.today().date()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["Date"] = df["datetime"].dt.date
    today_df = df[df["Date"] == today]

    st.subheader(f"📊 Mood Breakdown for {today}")
    mood_order = ["😠", "😐", "😊", "🎉"]
    mood_counts = today_df["mood"].value_counts().reset_index()
    mood_counts.columns = ["mood", "Count"]
    mood_counts["mood"] = pd.Categorical(mood_counts["mood"], categories=mood_order, ordered=True)
    mood_counts = mood_counts.sort_values("mood")
    fig = px.bar(mood_counts, x="mood", y="Count", text="Count",color_discrete_sequence=["#3639FF"])
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No mood data logged yet.")
