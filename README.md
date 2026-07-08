# Operations Reporting Platform — Palace Laundry Workflow Prototype

> **Disclaimer:** This is a demo portfolio project using sample/anonymised data only. It does not contain real company, customer, employee, financial or operational data.

Inspired by real operational workflows in hospitality laundry operations, this project uses only synthetic sample data (see [backend/seed.py](backend/seed.py)) — no real company, customer, employee, financial, or operational data is included or ever stored.

A full-stack internal-style management dashboard for hospitality laundry operations. The platform is designed to replace manual Excel workflows with structured data entry, automatic calculations, exportable reports, and backup support.

> **Status:** Working prototype, deployed as a public demo with sample data. See [Deployment](#deployment) below.

## What the platform does

The dashboard helps a laundry manager track key business operations in one place:

- Weekly income by customer
- Pool stock linen movement
- Petty cash vouchers and breakdowns
- Revenue performance and customer ranking
- Data quality checks
- Excel exports
- Local database backups

The system is designed for a single internal user first, with a future path toward hosted multi-user access.

## Key Features

### Weekly Income Entry
Enter Guest, Staff, and Flat laundry income per customer per week. The calendar auto-generates Monday–Sunday week ranges for each month, and monthly totals are calculated automatically.

### Pool Stock Tracking
Log daily linen movement per customer using predefined item templates. Quick Entry mode supports keyboard-only entry, with one item shown at a time and Enter used to advance through the list.

### Petty Cash Vouchers
Create digital petty cash vouchers with date, recipient, category, and line items. The breakdown layout matches accounting-style column structures and supports print formatting.

### Dashboard
View revenue KPIs, month-on-month comparison, service progress bars, customer revenue breakdown, pool stock summaries, recent activity, and backup status.

### Insights
Use preset query buttons to compare customers, compare periods, find the biggest mover, and identify missing data. The current version uses direct database queries rather than free-text AI.

### Performance
Rank customers by revenue, growth percentage, pool stock volume, and share of total revenue. Performance labels include Strong, Stable, and Needs Attention.

### Data Checks
Flag missing monthly data, zero totals, and duplicate packing list references.

### Excel Export
Export formatted `.xlsx` reports for monthly results, pool stock summaries, customer performance ranking, and petty cash breakdowns.

### Backup
Run manual backups and receive a daily 4pm reminder. Backups are saved as timestamped SQLite database copies to a configurable folder, such as OneDrive.

### Month Finalisation
Lock a month with a confirmation step. Any later edits require a written correction note, creating a simple audit trail.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | React 18 via CDN |
| Styling | Custom CSS |
| Excel Export | openpyxl |
| OCR | OCR.space API / Tesseract support |
| Runtime | Single local process |

## Repository Structure

```text
operations-reporting-dashboard/
├── backend/
│   ├── app.py              # Flask API
│   ├── db.py               # SQLite schema and database helpers
│   ├── seed.py             # Sample data loader
│   ├── requirements.txt    # Backend dependencies
│   └── .env.example        # Example environment variables
├── frontend/
│   └── index.html          # React frontend
├── docs/
│   ├── API.md              # API endpoint documentation
│   ├── ARCHITECTURE.md     # Technical architecture and decisions
│   ├── DATABASE.md         # Database schema notes
│   └── ROADMAP.md          # Known limitations and future plans
├── .gitignore
├── Procfile                # Start command for Railway/Heroku-style platforms
├── render.yaml              # Render blueprint (one-click deploy config)
├── LICENSE
└── README.md
```

## Setup

### Requirements

- Python 3.8+
- pip
- Google Chrome or another modern browser

### Run locally

```bash
# 1. Clone the repository
git clone https://github.com/simrandocx/operations-reporting-dashboard.git
cd operations-reporting-dashboard/backend

# 2. Create and activate a virtual environment
python3 -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) copy the env template if you want to set an OCR key or
#    change the backup folder locally
cp .env.example .env

# 5. Start the Flask server — it seeds sample data automatically on boot
python app.py
```

Then open:

```text
http://127.0.0.1:5001/app
```

## Configuration

All configuration is via environment variables, loaded from `backend/.env`
locally (via `python-dotenv`) or set directly by your hosting platform in
production. See `backend/.env.example` for the full list with explanations.
Nothing sensitive is hardcoded in the source — the OCR API key in
particular must never be committed.

| Variable | Default | Purpose |
|---|---|---|
| `OCR_SPACE_API_KEY` | *(empty)* | OCR.space API key. Feature quietly disables itself when unset. |
| `BACKUP_DIR` | `backups` | Where manual backups are copied to. |
| `DB_PATH` | `backend/operations_demo.db` | SQLite file location. Point at a persistent disk in production. |
| `DEMO_MODE` | `true` | Reseeds sample data on every restart + enables the in-app "Reset demo data" button. |
| `PORT` | `5001` | Port the server listens on (most platforms set this for you). |
| `FLASK_DEBUG` | `false` | Flask debug mode. Keep `false` for any public deployment. |
| `ALLOWED_ORIGIN` | `*` | CORS origin allowed to call the API. |

## Deployment

This is deployed as a **public read/write demo with synthetic sample data
only** — see the disclaimer at the top of this README. It is not the real
internal business version.

### Platform: Render

Of the common simple options (Render, Railway, PythonAnywhere), **Render**
is the best fit here: it has a real free tier for a Python web service,
deploys straight from GitHub with zero extra config (a `render.yaml`
blueprint is included in this repo), and — unlike PythonAnywhere's free
tier — allows outbound HTTP calls, which the OCR.space integration needs.
Railway is also workable but no longer has a permanent free tier.

**Steps:**

1. Push this repository to GitHub (see the [pre-publish checklist](#before-making-this-public) below first).
2. Go to [render.com](https://render.com) → **New** → **Blueprint**, and point it at this repo. Render will read `render.yaml` and configure the service automatically.
   - No blueprint? Create a **New Web Service** manually instead:
     - **Root Directory:** repo root
     - **Build Command:** `pip install -r backend/requirements.txt`
     - **Start Command:** `gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT`
3. Under **Environment**, set any variables you want to override (e.g. `OCR_SPACE_API_KEY` if you want OCR enabled in the demo — optional, and safe to leave blank).
4. Deploy. Render builds, installs dependencies, and starts the app. The first request may take a few seconds on the free tier (cold start after inactivity).
5. Your demo will be live at `https://<your-service-name>.onrender.com/app`.

### SQLite persistence on Render's free tier

Render's free web service tier does **not** provide a persistent disk —
the filesystem is wiped on every new deploy and container restart. For a
**public demo with only sample data**, this is actually the right
behavior, not a risk to work around:

- This repo runs in **reset-on-start mode** (`DEMO_MODE=true` by default): every time the app boots, `backend/seed.py` re-populates the database with the same synthetic sample data.
- There's also an in-app **"Reset demo data"** button (sidebar) that calls `POST /api/demo-reset`, so if a visitor's testing leaves the data looking messy, anyone can restore it instantly without redeploying.
- Because nothing here is real data, losing "changes" on restart costs nothing — it's the simplest option and needs no extra infrastructure.

If you later want the demo's edits to persist between restarts (still with
sample data, not real data), you have two options, in order of effort:

1. **Add a Render persistent disk** (~$1/mo on Render's paid plans) and set `DB_PATH` to a path on that disk. No code changes needed — `DB_PATH` is already read from the environment.
2. **Migrate to PostgreSQL** for a real multi-user, persistent setup (Render has a free Postgres tier). This is a bigger change — you'd swap `sqlite3` calls in `backend/db.py` for `psycopg2`/SQLAlchemy — and is really only worth doing if this stops being "just a demo." The `docs/ROADMAP.md` already flags this as the long-term path for a real deployment.

For this demo, option zero (reset-on-start, as shipped) is the right call.

## Documentation

- [API Endpoints](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Database Schema](docs/DATABASE.md)
- [Roadmap](docs/ROADMAP.md)

## Known Limitations

- Public demo instance resets its data on every restart (see [Deployment](#deployment)) — this is intentional.
- No authentication (fine for a read-mostly public demo of sample data; would be required before handling anything real).
- SQLite is not ideal for multi-user cloud deployment at real-world scale.
- OCR accuracy depends heavily on image quality and packing list layout, and OCR is disabled in the public demo by default.
- Historical spreadsheet import still needs to be added.

## Roadmap

- Import historical spreadsheet data
- Add authentication
- Add OneDrive or cloud backup integration for a real (non-demo) deployment
- Improve OCR using a vision model
- Add price list tracking
- Add PDF exports
- Migrate from SQLite to PostgreSQL for a persistent, multi-user deployment

## Before making this public

Checklist to run through before pushing this repo public / sharing the link:

- [ ] `backend/.env` is **not** committed (check `git status` — only `.env.example` should be tracked).
- [ ] No real `.db` files are committed (`git ls-files | grep '\.db$'` should return nothing).
- [ ] `backend/backups/` and `backend/uploads/` are empty or gitignored, not committed.
- [ ] `git log` / `git grep` show no real company, customer, or employee names anywhere in history — if in doubt, start from a fresh repo rather than trying to scrub history.
- [ ] `DEMO_MODE=true` is set on the deployed instance (it's the default).
- [ ] `FLASK_DEBUG=false` on the deployed instance (Flask's debugger must never be exposed publicly).
- [ ] `OCR_SPACE_API_KEY` is either left blank on the public deployment, or set as a platform environment variable — never hardcoded in `app.py`.
- [ ] The disclaimer at the top of this README and the in-app "Demo mode" banner are both present and accurate.
- [ ] Loaded the deployed URL once yourself and confirmed only sample data (`Hotel A`, `Hotel B`, …) appears anywhere in the UI and in Excel exports.

## License

This project is licensed under the MIT License.

