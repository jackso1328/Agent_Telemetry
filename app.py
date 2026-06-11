import streamlit as st
import pymongo
import certifi
import pandas as pd
import os
from bson import ObjectId
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- 0. SECURITY & ENV SETUP ---
# Load sensitive keys from .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
API_KEY = os.getenv("API_KEY")

# --- 1. UI SETUP (Premium Dashboard Restored) ---
st.set_page_config(page_title="TelemetryGuard | Command Center", layout="wide", page_icon="🛡️")

# Restored the Advanced CSS for the Sea Blue & Lavender aesthetic, hover effects, and log boxes
st.markdown("""
    <style>
    .stApp { background-color: #F8F8FF; color: #2E2E38; }
    
    h1 { 
        background: -webkit-linear-gradient(45deg, #006994, #967BB6); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        font-weight: 800; 
    }
    
    div[data-testid="metric-container"] { 
        background-color: #FFFFFF; 
        border: 2px solid #E6E6FA; 
        padding: 5% 10% 5% 10%; 
        border-radius: 12px; 
        box-shadow: 0 4px 15px rgba(0, 105, 148, 0.08); 
        transition: transform 0.2s ease; 
    }
    div[data-testid="metric-container"]:hover { transform: translateY(-2px); }
    
    div.stButton > button { 
        background: linear-gradient(90deg, #006994 0%, #967BB6 100%); 
        color: white !important; 
        border: none; border-radius: 8px; padding: 15px 30px; 
        font-weight: bold; font-size: 16px; letter-spacing: 1px; 
        transition: all 0.3s ease; width: 100%; 
        box-shadow: 0 4px 10px rgba(150, 123, 182, 0.3); 
    }
    div.stButton > button:hover { 
        box-shadow: 0 6px 15px rgba(0, 105, 148, 0.4); 
        transform: scale(1.02); 
    }
    
    .stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .stMarkdown pre { background-color: white !important; border-left: 4px solid #0077B6; padding: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ TelemetryGuard: Command Center")
st.markdown("**Autonomous SRE platform powered by real-time Z-Scores and LLM orchestration.**")
st.divider()

# --- 2. DATABASE CONNECTION ---
@st.cache_resource
def init_db():
    if not MONGO_URI:
        st.error("🚨 MONGO_URI not found! Please check your .env file.")
        return None
    try:
        client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        return client["environmental_monitoring"]
    except Exception as e:
        st.error(f"🚨 Database connection failed: {e}")
        return None

db = init_db()

# Stop execution gracefully if DB fails to connect
if db is None:
    st.stop()

raw_collection = db["raw_telemetry"]
alerts_collection = db["system_alerts"]

# --- 3. THE NATIVE PYTHON TOOLS ---
def fetch_unverified_telemetry() -> list:
    docs = list(raw_collection.find({"status": "unverified"}))
    for doc in docs: doc["_id"] = str(doc["_id"])
    return docs

def get_sensor_baseline(device_id: str) -> dict:
    baselines = {
        "AQI_SENSOR_001": {"mean": 35.0, "std_dev": 2.5},
        "AQI_SENSOR_002": {"mean": 40.0, "std_dev": 4.1},
        "AQI_SENSOR_003": {"mean": 38.5, "std_dev": 3.0}
    }
    return baselines.get(device_id, {"mean": 0, "std_dev": 1})

def flag_corrupted_device(document_id: str, dynamic_reason: str) -> str:
    raw_collection.update_one(
        {"_id": ObjectId(document_id)},
        {"$set": {"status": "Flagged_Anomaly", "anomaly_reason": dynamic_reason}}
    )
    return "Status updated."

def log_remediation_ticket(device_id: str, alert_details: str, remediation_code: str) -> str:
    ticket = {
        "device_id": device_id,
        "issue_detected": alert_details,
        "auto_remediation_script": remediation_code,
        "resolution_status": "Open - Code Generated"
    }
    alerts_collection.insert_one(ticket)
    return "Ticket and code logged."

# --- 4. STREAMLIT DASHBOARD LAYOUT ---

# Top Row: Live KPIs
m1, m2, m3 = st.columns(3)
total_docs = raw_collection.count_documents({})
flagged_docs = raw_collection.count_documents({"status": "Flagged_Anomaly"})
open_tickets = alerts_collection.count_documents({})

m1.metric("Total Sensor Pings", f"{total_docs}")
m2.metric("Critical Anomalies Detected", f"{flagged_docs}", delta=f"{flagged_docs} Unstable", delta_color="inverse")
m3.metric("Auto-Remediations Logged", f"{open_tickets}")

st.write("---")

# Middle Row: Data & Action
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📡 Live Telemetry Feed")
    df = pd.DataFrame(list(raw_collection.find()))
    
    if not df.empty:
        df['_id'] = df['_id'].astype(str)
        
        # Restored: Visual Bar Chart for PM2.5
        st.markdown("<span style='color:#967BB6; font-weight:bold;'>Current PM2.5 Saturation</span>", unsafe_allow_html=True)
        chart_data = df[['device_id', 'metrics']].dropna()
        if not chart_data.empty and isinstance(chart_data['metrics'].iloc[0], dict):
             pm_data = [{"Device": row['device_id'], "PM2.5": row['metrics'].get('pm2_5', 0)} for idx, row in chart_data.iterrows() if row['metrics'].get('pm2_5') is not None]
             if pm_data:
                 st.bar_chart(pd.DataFrame(pm_data).set_index("Device"), color="#006994")
                 
        # Raw Data Table
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No data in raw_telemetry collection.")

with col2:
    st.subheader("🧠 Intelligence Core")
    st.markdown("Initialize the AI to run statistical Z-Score evaluations against the live database.")
    
    if st.button("⚡ EXECUTE AUTONOMOUS AUDIT"):
        if not API_KEY:
            st.error("🚨 API_KEY not found! Please check your .env file.")
            st.stop()
            
        with st.status("Agent Operational: Scanning Database...", expanded=True) as status:
            st.write("📡 Handshaking with MongoDB Atlas...")
            
            ai_client = genai.Client(api_key=API_KEY)
            available_tools = [fetch_unverified_telemetry, get_sensor_baseline, flag_corrupted_device, log_remediation_ticket]
            
            system_instruction = """
            You are an Autonomous SRE Agent. 
            1. Call 'fetch_unverified_telemetry'.
            2. For each document, call 'get_sensor_baseline' to get historical mean and std_dev.
            3. Calculate the Z-score for pm2_5: Z = (pm2_5 - mean) / std_dev.
            4. If the absolute Z-score is > 3, or if the metric is missing (null), it is an anomaly.
            5. If anomalous, call 'flag_corrupted_device' passing the document ID and your reasoning.
            6. Then, call 'log_remediation_ticket' with the device_id, issue, AND write a short Python script meant to remotely reboot the sensor hardware.
            7. Provide a detailed summary log of your mathematical reasoning.
            """
            
            st.write("🧠 Executing Z-Score Analysis & Generating Code...")
            
            # Using the highly capable 2.5-flash model
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash', 
                contents='Perform the statistical database audit now.',
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=available_tools,
                    temperature=0.1
                )
            )
            
            status.update(label="Audit Complete & DB Secured!", state="complete", expanded=False)
        
        st.success("Target neutralized. Database updated successfully.")
        st.balloons() 
        
        # Display the reasoning output cleanly
        with st.expander("🔍 View Internal SRE Logs & Generated Scripts", expanded=True):
            st.write(response.text)