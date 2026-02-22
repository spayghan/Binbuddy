import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ================= CONFIGURATION =================
BLYNK_TOKEN = "cQSNlwy4EcEG_vGe1sCbugE0aTXk4NE0"
BLYNK_URL = f"https://blr1.blynk.cloud/external/api/get?token={BLYNK_TOKEN}"

# Email settings
SENDER = "tusharganmukhe@gmail.com"
PASS = ""
RECEIVER = "tusharganmukhe5580@gmail.com"

# Session history
if 'history_df' not in st.session_state:
    st.session_state.history_df = pd.DataFrame(columns=['Time', 'Level'])
if 'alert_sent' not in st.session_state:
    st.session_state.alert_sent = False

def get_blynk_data():
    try:
        # Fetching V1 from BLR1 Server
        res = requests.get(BLYNK_URL + "&v1", timeout=2)
        val = res.text.strip('[]" ')
        return float(val) if val else 0.0
    except:
        return None

def send_alert(level):
    if not st.session_state.alert_sent:
        try:
            msg = MIMEMultipart()
            msg['Subject'] = f"🚨 URGENT: BinBuddy Alert - {level}% Full"
            msg.attach(MIMEText(f"BinBuddy at 22cm capacity is {level}% full. Collection required.", 'plain'))
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(SENDER, PASS)
            server.sendmail(SENDER, RECEIVER, msg.as_string())
            server.quit()
            st.session_state.alert_sent = True
            st.toast("Email Notification Sent!")
        except:
            pass

# ================= DASHBOARD UI =================
st.set_page_config(page_title="BinBuddy Analytics", layout="wide")
st.title("🗑️ BinBuddy: Precision Analytics Dashboard")

col1, col2 = st.columns([1, 2])
metric_loc = col1.empty()
status_loc = col1.empty()
chart_loc = col2.empty()

while True:
    current_val = get_blynk_data()
    
    if current_val is not None:
        now = datetime.now().strftime("%H:%M:%S")
        
        # Add to historical analytics
        new_row = pd.DataFrame({'Time': [now], 'Level': [current_val]})
        st.session_state.history_df = pd.concat([st.session_state.history_df, new_row], ignore_index=True)
        if len(st.session_state.history_df) > 30:
            st.session_state.history_df = st.session_state.history_df.iloc[1:]

        # Update Indicators
        metric_loc.metric("Accurate Fill Level", f"{current_val:.1f}%")
        
        if current_val >= 90:
            status_loc.error("CRITICAL: BIN FULL")
            send_alert(current_val)
        elif current_val < 20:
            status_loc.success("STATUS: OPTIMAL")
            st.session_state.alert_sent = False 

        # Update Trend Chart
        fig = px.area(st.session_state.history_df, x='Time', y='Level', 
                      title="Real-Time Analytics (22cm Bin Logic)")
        fig.update_yaxes(range=[-2, 102]) # Ensures graph scale doesn't flicker
        chart_loc.plotly_chart(fig, width="stretch")
        
        # Print to Terminal for debugging
        print(f"[{now}] Receiving V1: {current_val}%")

    time.sleep(2)