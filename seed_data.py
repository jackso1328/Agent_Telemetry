import pymongo
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()
URI = os.getenv("MONGO_URI")

def seed_database():
    if not URI:
        print("Error: MONGO_URI not found in environment variables.")
        return
        
    print("Connecting to MongoDB Atlas...")
    client = pymongo.MongoClient(URI)
    
    # Access the database and collection
    db = client["environmental_monitoring"]
    collection = db["raw_telemetry"]
    
    # Clear out any old test data
    collection.delete_many({})
    
    # Simulated IoT Air Quality payloads
    mock_data = [
        # 1. Normal Reading
        {
            "device_id": "AQI_SENSOR_001",
            "timestamp": datetime.now(timezone.utc),
            "metrics": {"pm2_5": 35.2, "co2_ppm": 410, "humidity": 45},
            "status": "unverified"
        },
        # 2. Anomaly: Extreme Mathematical Outlier (Sensor Malfunction)
        {
            "device_id": "AQI_SENSOR_002",
            "timestamp": datetime.now(timezone.utc),
            "metrics": {"pm2_5": 9999.9, "co2_ppm": 8500, "humidity": 12}, 
            "status": "unverified"
        },
        # 3. Anomaly: Missing Data Vectors (Network Drop)
        {
            "device_id": "AQI_SENSOR_003",
            "timestamp": datetime.now(timezone.utc),
            "metrics": {"pm2_5": None, "co2_ppm": 405}, # Missing humidity
            "status": "unverified"
        }
    ]
    
    print("Injecting telemetry payloads...")
    collection.insert_many(mock_data)
    print(f"Successfully inserted {len(mock_data)} records into 'raw_telemetry'.")
    
    client.close()

if __name__ == "__main__":
    seed_database()