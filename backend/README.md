# Backend

Flask backend for the Laundry Manager Dashboard.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed.py
python app.py
```

The app should run at:

```text
http://127.0.0.1:5001/app
```

## Main files

| File | Purpose |
|---|---|
| `app.py` | Flask API routes |
| `db.py` | SQLite schema and connection helpers |
| `seed.py` | Sample data loader |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |
