# MiniSOC — Security Operations Center

MiniSOC is a Flask-based cybersecurity project that demonstrates a Security Operations Center (SOC) for monitoring security events, detecting threats and generating alerts.

## Features

- Security monitoring dashboard
- Event simulator
- Rule-based detection engine
- Automatic alert generation
- Log Explorer
- Detector Rules
- Threat Intelligence
- Security Reports
- Login authentication
- India-focused 3D threat visualization

## Technology

- Python
- Flask
- SQLite
- HTML / CSS / JavaScript
- Globe.gl

## Project Flow

```text
Event Simulator
      ↓
SQLite Database
      ↓
Detection Engine
      ↓
Detector Rules
      ↓
Alerts
      ↓
Dashboard / Reports```



## Run Locally

python -m venv --without-pip venv
.\venv\Scripts\Activate.ps1
python -m ensurepip --upgrade
python -m pip install -r requirements.txt
python app.py

Open:

http://127.0.0.1:5000

# Default Login

Username: admin
Password: Admin@12345

## Disclaimer

MiniSOC is an educational cybersecurity project intended for authorized local testing and demonstration.

## Author

M Archana
Cybersecurity Student