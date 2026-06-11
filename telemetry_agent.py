import os
import pymongo
import certifi
from bson import ObjectId
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is missing from the environment variables.")

# Establish direct database connection WITH the SSL certificate fix
client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["environmental_monitoring"]
raw_collection = db["raw_telemetry"]
alerts_collection = db["system_alerts"]

# Define the Native Database Tools for the Agent
def fetch_unverified_telemetry() -> list:
    """Retrieves all sensor records from raw_telemetry that are unverified."""
    print("\n[Tool Executing] Fetching unverified data documents...")
    docs = list(raw_collection.find({"status": "unverified"}))
    for doc in docs:
        doc["_id"] = str(doc["_id"]) # Convert ObjectId to string for JSON compatibility
    return docs

def flag_corrupted_device(document_id: str, dynamic_reason: str) -> str:
    """Updates a document status to 'Flagged_Anomaly' based on its ID."""
    print(f"\n[Tool Executing] Flagging document {document_id} due to: {dynamic_reason}")
    result = raw_collection.update_one(
        {"_id": ObjectId(document_id)},
        {"$set": {"status": "Flagged_Anomaly", "anomaly_reason": dynamic_reason}}
    )
    return f"Modified count: {result.modified_count}"

def log_remediation_ticket(device_id: str, alert_details: str) -> str:
    """Inserts an automated SRE incident ticket into the system_alerts collection."""
    print(f"\n[Tool Executing] Logging SRE ticket for {device_id}...")
    ticket = {
        "device_id": device_id,
        "issue_detected": alert_details,
        "resolution_status": "Open",
        "severity": "Critical"
    }
    result = alerts_collection.insert_one(ticket)
    return f"Created ticket with ID: {str(result.inserted_id)}"

# Orchestrate the Autonomous Loop
def run_native_agent():
    print("Initializing TelemetryGuard Native Python Agent...")
    
    # Initialize the GenAI client (picks up GEMINI_API_KEY from environment)
    ai_client = genai.Client()
    
    system_instruction = """
    You are an Autonomous SRE Agent. Your mission is to audit the 'environmental_monitoring' database.
    1. Call 'fetch_unverified_telemetry' to get all unverified telemetry documents.
    2. Loop through each document and inspect its metrics. 
    3. If 'pm2_5' is above 500 or if any core metric value is missing (None/null), treat it as an anomaly.
    4. For any anomaly found, immediately call 'flag_corrupted_device' passing the document's string ID and a brief description of the issue.
    5. Following that, call 'log_remediation_ticket' to register a ticket in the system alerts collection for that device.
    6. Provide a clean summary log of your findings when finished.
    """
    
    # Bundle functions as executable tools
    available_tools = [fetch_unverified_telemetry, flag_corrupted_device, log_remediation_ticket]
    
    print("Agent is beginning the autonomous database audit loop...")
    
    # Execute with automatic tool resolution enabled
    response = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Perform the full database pipeline audit now.',
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=available_tools,
            temperature=0.2
        )
    )
    
    print("\n================= AGENT SUMMARY LOG =================")
    print(response.text)
    print("=====================================================")

if __name__ == "__main__":
    run_native_agent()