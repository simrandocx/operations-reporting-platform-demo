"""Seed with sample data. Run: python seed.py"""
from db import init_db, get_conn
import random, calendar
from datetime import date, timedelta

init_db()
conn = get_conn()

conn.executescript("""
DELETE FROM pool_stock;
DELETE FROM daily_results;
DELETE FROM monthly_status;
DELETE FROM hotels;
""")
conn.commit()

hotels_data = [
    ("Ham Yard Hotel",         "hotel"),
    ("Haymarket Hotel",        "hotel"),
    ("The Soho Hotel",         "hotel"),
    ("Covent Garden Hotel",    "hotel"),
    ("Charlotte Street Hotel", "hotel"),
    ("Number Sixteen",         "hotel"),
    ("Dorset Square Hotel",    "hotel"),
    ("Knightsbridge Hotel",    "hotel"),
    ("NoMad Hotel",            "outside_contract"),
    ("Shangri-La The Shard",   "outside_contract"),
]
conn.executemany("INSERT INTO hotels (name, customer_type) VALUES (?,?)", hotels_data)
conn.commit()

hotels = conn.execute("SELECT * FROM hotels").fetchall()
print(f"Created {len(hotels)} customers.")


def get_weeks(year, month):
    first = date(year, month, 1)
    last  = date(year, month, calendar.monthrange(year, month)[1])
    weeks, current, n = [], first, 1
    while current <= last:
        days_until_sunday = 6 - current.weekday()
        week_end = min(current + timedelta(days=days_until_sunday), last)
        if current.month == week_end.month:
            label = f"{current.day}–{week_end.day} {current.strftime('%b')}"
        else:
            label = f"{current.day} {current.strftime('%b')}–{week_end.day} {week_end.strftime('%b')}"
        weeks.append((current.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d"), label))
        current = week_end + timedelta(days=1)
        n += 1
    return weeks


random.seed(42)
months = [(2025, 1), (2025, 2), (2025, 3)]
count = 0
for year, month in months:
    weeks = get_weeks(year, month)
    for h in hotels:
        base = random.uniform(200, 1200)
        for week_start, week_end, label in weeks:
            conn.execute("""
                INSERT INTO daily_results
                  (hotel_id, entry_date, week_end_date, week_label,
                   guest_laundry_income, staff_laundry_income, flat_laundry_income, notes)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                h["id"], week_start, week_end, label,
                round(random.uniform(50, base), 2),
                round(random.uniform(20, base * 0.4), 2),
                round(random.uniform(0,  base * 0.3), 2),
                "",
            ))
            count += 1
        if (year, month) != (2025, 3):
            conn.execute("""
                INSERT INTO monthly_status (hotel_id, year, month, status)
                VALUES (?,?,?,?)
            """, (h["id"], year, month, "checked"))
conn.commit()
print(f"Created {count} weekly entries across {len(months)} months.")
conn.close()
print("\nDone. Start the server: python app.py")
