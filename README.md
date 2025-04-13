# EV-chargin
# EV Charging System for Apartments

A web app to manage electric vehicle charging in apartment complexes, with separate dashboards for vehicle owners and building management.

## Features

- 🚗 Vehicle owner dashboard
- 🔌 Charging schedule entry
- 💰 Monthly billing
- 👮 Management control panel
- 🛑 Block/unblock users for unpaid dues

## Tech Stack

- Python (Flask)
- SQLite
- HTML/CSS
- Bootstrap (optional)

## Setup

```bash
git clone https://github.com/your-username/ev-charging-system.git
cd ev-charging-system
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sqlite3 instance/database.db < schema.sql
python run.py
