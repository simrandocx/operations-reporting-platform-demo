import sqlite3, os, time
from threading import Lock

# DB_PATH can be overridden via the DB_PATH environment variable so the app
# can point at a persistent disk / mounted volume in production. Defaults to
# a local file next to this module, which is fine for local dev and for
# demo deployments that reset on every restart.
DB_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(os.path.dirname(__file__), "operations_demo.db"),
)

# When SANDBOX_MODE is on (the default in DEMO_MODE), every visitor gets
# their own private, in-memory copy of the database on their first write or
# read. Their edits only ever happen in that copy: the real on-disk demo
# data is never modified by a site visitor, and visitors never see each
# other's changes. Sandboxes are cheap (the demo dataset is tiny) and are
# capped at MAX_SANDBOX_SESSIONS, evicting the least-recently-used one once
# the cap is hit, so memory use stays bounded on a long-running deployment.
SANDBOX_MODE = os.environ.get("DEMO_MODE", "true").lower() in ("1", "true", "yes")
MAX_SANDBOX_SESSIONS = int(os.environ.get("MAX_SANDBOX_SESSIONS", "50"))

_sandbox_lock = Lock()
_sandbox_sessions = {}  # session_id -> {"conn": sqlite3.Connection, "last_used": float}


class _SandboxConnProxy:
    """Wraps a visitor's long-lived in-memory connection so that route code
    calling conn.close() (as every route does for the real database) simply
    returns the connection to the pool instead of destroying it — an
    in-memory SQLite database disappears the moment its one connection is
    closed, so a real close() would wipe the visitor's sandbox after their
    very first request. Everything else passes straight through.
    """
    def __init__(self, conn):
        self.__dict__["_conn"] = conn

    def close(self):
        pass  # keep the sandbox alive for the rest of the visitor's session

    def __getattr__(self, name):
        return getattr(self._conn, name)


def _clone_from_disk():
    mem = sqlite3.connect(":memory:", check_same_thread=False)
    mem.row_factory = sqlite3.Row
    src = sqlite3.connect(DB_PATH)
    src.backup(mem)
    src.close()
    mem.execute("PRAGMA foreign_keys = ON")
    return mem


def reset_sandbox(session_id):
    """Discards one visitor's sandbox so their next request starts again
    from a fresh clone of the real demo data. Only ever touches that one
    visitor's in-memory copy — never the on-disk database, never anyone
    else's sandbox."""
    with _sandbox_lock:
        entry = _sandbox_sessions.pop(session_id, None)
    if entry:
        entry["conn"].close()


def _current_sandbox_id():
    """Reads the current visitor's sandbox id from Flask's request context,
    if any. Returns None outside of a request (app startup, seeding, the
    `python seed.py` CLI) so those always talk to the real on-disk database."""
    try:
        from flask import g, has_request_context
        if has_request_context():
            return getattr(g, "sandbox_id", None)
    except RuntimeError:
        pass
    return None


def get_conn():
    """Returns a database connection.

    - Outside a Flask request (app startup, seeding, the seed.py CLI), or
      when SANDBOX_MODE is off: connects to the real on-disk database,
      exactly as before — every existing call site in app.py keeps working
      unchanged.
    - Inside a request, when SANDBOX_MODE is on: transparently returns the
      current visitor's private in-memory database (see module docstring),
      cloned from the on-disk demo data the first time it's needed and
      reused for the rest of their session.
    """
    session_id = _current_sandbox_id() if SANDBOX_MODE else None

    if not session_id:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    with _sandbox_lock:
        entry = _sandbox_sessions.get(session_id)
        if entry is None:
            if len(_sandbox_sessions) >= MAX_SANDBOX_SESSIONS:
                oldest_sid = min(_sandbox_sessions, key=lambda k: _sandbox_sessions[k]["last_used"])
                _sandbox_sessions.pop(oldest_sid)["conn"].close()
            entry = {"conn": _clone_from_disk(), "last_used": time.time()}
            _sandbox_sessions[session_id] = entry
        entry["last_used"] = time.time()
        return _SandboxConnProxy(entry["conn"])


def get_disk_conn():
    """Always connects to the real on-disk database, bypassing sandboxing
    entirely. Used by init_db() and seed.py, which must always operate on
    the real demo data regardless of request context."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_disk_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        customer_type TEXT NOT NULL CHECK(customer_type IN ('hotel','outside_contract')),
        active_status INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS daily_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_id INTEGER NOT NULL REFERENCES hotels(id),
        entry_date TEXT NOT NULL,
        week_end_date TEXT NOT NULL DEFAULT '',
        week_label TEXT NOT NULL DEFAULT '',
        guest_laundry_income REAL NOT NULL DEFAULT 0,
        staff_laundry_income REAL NOT NULL DEFAULT 0,
        flat_laundry_income REAL NOT NULL DEFAULT 0,
        notes TEXT DEFAULT '',
        UNIQUE(hotel_id, entry_date)
    );

    CREATE TABLE IF NOT EXISTS monthly_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_id INTEGER NOT NULL REFERENCES hotels(id),
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'in_progress'
            CHECK(status IN ('in_progress','ready_for_checking','checked','finalised')),
        correction_note TEXT DEFAULT '',
        UNIQUE(hotel_id, year, month)
    );

    CREATE TABLE IF NOT EXISTS pool_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_id INTEGER NOT NULL REFERENCES hotels(id),
        entry_date TEXT NOT NULL,
        linen_item TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        packing_list_ref TEXT DEFAULT '',
        notes TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS price_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_id INTEGER NOT NULL REFERENCES hotels(id),
        item_name TEXT NOT NULL,
        service_type TEXT NOT NULL,
        unit_price REAL NOT NULL,
        effective_from TEXT NOT NULL,
        active_status INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS petty_cash_vouchers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voucher_date TEXT NOT NULL,
        required_for TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'Misc',
        passed_by TEXT DEFAULT '',
        signature TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        total_amount REAL NOT NULL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS petty_cash_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voucher_id INTEGER NOT NULL REFERENCES petty_cash_vouchers(id),
        description TEXT NOT NULL DEFAULT '',
        amount_gbp REAL NOT NULL DEFAULT 0,
        gross REAL DEFAULT 0,
        vat REAL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS scanned_packing_lists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_id INTEGER NOT NULL REFERENCES hotels(id),
        entry_date TEXT NOT NULL,
        image_filename TEXT NOT NULL,
        raw_ocr_text TEXT DEFAULT '',
        status TEXT NOT NULL DEFAULT 'pending_review'
            CHECK(status IN ('pending_review','confirmed','discarded')),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()


def row_to_dict(row):
    return dict(row) if row else None


def rows_to_list(rows):
    return [dict(r) for r in rows]
