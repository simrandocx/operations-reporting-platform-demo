import sqlite3, os

# DB_PATH can be overridden via the DB_PATH environment variable so the app
# can point at a persistent disk / mounted volume in production. Defaults to
# a local file next to this module, which is fine for local dev and for
# demo deployments that reset on every restart.
DB_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(os.path.dirname(__file__), "operations_demo.db"),
)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
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
