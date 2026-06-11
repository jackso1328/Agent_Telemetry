<div align="center">

# 🛡️ TelemetryGuard
### Autonomous SRE Command Center for Industrial IoT

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10-green.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-brightgreen.svg)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange.svg)

**Stop manual sensor monitoring. Start autonomous self-healing.**

</div>

---

## 🎯 The Problem
Industrial facilities manage thousands of sensors. Conventional monitoring relies on static thresholds, leading to:
* 📉 **Alert Fatigue:** Engineers drowning in false-positive notifications.
* ⏳ **Slow Response:** Hardware degradation often goes unnoticed until failure.
* 💸 **Downtime Costs:** Manual troubleshooting is reactive, not predictive.

---

## 🚀 The Solution
TelemetryGuard leverages **Agentic AI** to move from reactive alerts to autonomous resolution.

*(Screenshot: Add an image of your architecture or data flow here)*

### 🧠 How It Works
1. **Statistical Profiling:** Calculates rolling Z-scores ($Z = \frac{x - \mu}{\sigma}$) to detect anomalies, not just standard spikes.
2. **Autonomous Auditing:** The Gemini 2.5 AI agent performs a deep database scan every time the audit is triggered.
3. **Self-Healing Code:** When a failure is found, the agent writes, validates, and logs a Python/Bash remediation script to reboot the specific hardware.

---

## 📊 Dashboard Interaction
*A premium, sea blue and lavender SRE dashboard to visualize infrastructure health in real-time.*

| Feature | Description |
| :--- | :--- |
| **Live Telemetry** | Streamed sensor data with auto-refresh and PM2.5 saturation charts. |
| **Intelligence Core** | AI-driven analysis with mathematical reasoning logs. |
| **Auto-Remediation** | Instant log creation and targeted script generation. |

*(Screenshot: Add an image of your Streamlit Dashboard here)*

---

## 🛠️ Tech Stack
* **Intelligence:** Google Gemini 2.5 Flash (Function Calling)
* **Interface:** Streamlit
* **Database:** MongoDB Atlas
* **Data Science:** Pandas & NumPy

---

## 📋 Quick Start Guide for Judges

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/TelemetryGuard.git](https://github.com/your-username/TelemetryGuard.git)
   cd TelemetryGuard

2. Install dependencies:
   pip install -r requirements.txt

3. Environment Setup:

   Rename the provided .env.example file to .env.

   Open the .env file and replace the placeholder text with your own Google Gemini API Key and MongoDB URI.

   Run the Application:

      streamlit run app.py
