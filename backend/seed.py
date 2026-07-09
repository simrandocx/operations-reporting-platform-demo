"""Seed / reset the database with sample data only.

This file contains NO real company, customer, employee, or financial data.
All hotel names ("Hotel A", "Outside Contract A", etc.) and figures are
synthetic, generated with a fixed random seed for repeatable demo output.

Run directly:  python seed.py
Or import:     from seed import seed_demo_data
"""
import random
import calendar
from datetime import date, timedelta

from db import init_db, get_disk_conn

LINEN_ITEMS = [
    "Bath Towels", "Hand Towels", "Bath Mats",
    "King Sheets", "Double Sheets", "Pillowcases", "Duvet Covers",
]

PETTY_CASH_CATEGORIES = ["Canteen Food", "Postage", "Cleaning", "Misc", "Travel"]


def _get_weeks(year, month):
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])
    weeks, current = [], first
    while current <= last:
        days_until_sunday = 6 - current.weekday()
        week_end = min(current + timedelta(days=days_until_sunday), last)
        if current.month == week_end.month:
            label = f"{current.day}\u2013{week_end.day} {current.strftime('%b')}"
        else:
            label = f"{current.day} {current.strftime('%b')}\u2013{week_end.day} {week_end.strftime('%b')}"
        weeks.append((current.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d"), label))
        current = week_end + timedelta(days=1)
    return weeks


def seed_demo_data(verbose=True):
    """(Re)creates all tables and fills them with synthetic sample data.
    Safe to call repeatedly -- it wipes existing rows first, so this also
    works as a "reset demo data" action for a public deployment.
    """
    init_db()
    conn = get_disk_conn()

    conn.executescript("""
        DELETE FROM scanned_packing_lists;
        DELETE FROM petty_cash_items;
        DELETE FROM petty_cash_vouchers;
        DELETE FROM pool_stock;
        DELETE FROM daily_results;
        DELETE FROM monthly_status;
        DELETE FROM hotels;
    """)
    conn.commit()

    hotels_data = [
        ("Hotel A", "hotel"), ("Hotel B", "hotel"), ("Hotel C", "hotel"),
        ("Hotel D", "hotel"), ("Hotel E", "hotel"), ("Hotel F", "hotel"),
        ("Hotel G", "hotel"), ("Hotel H", "hotel"),
        ("Outside Contract A", "outside_contract"),
        ("Outside Contract B", "outside_contract"),
    ]
    conn.executemany("INSERT INTO hotels (name, customer_type) VALUES (?,?)", hotels_data)
    conn.commit()

    hotels = conn.execute("SELECT * FROM hotels").fetchall()
    if verbose:
        print(f"Created {len(hotels)} sample customers.")

    random.seed(42)
    months = [(2025, 1), (2025, 2), (2025, 3)]
    result_count = 0
    pool_count = 0

    for year, month in months:
        weeks = _get_weeks(year, month)
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
                    round(random.uniform(0, base * 0.3), 2),
                    "",
                ))
                result_count += 1

                # A few sample pool stock (linen movement) rows per week
                for item in random.sample(LINEN_ITEMS, k=3):
                    conn.execute("""
                        INSERT INTO pool_stock
                          (hotel_id, entry_date, linen_item, quantity, packing_list_ref, notes)
                        VALUES (?,?,?,?,?,?)
                    """, (
                        h["id"], week_start, item,
                        random.randint(10, 250),
                        f"PL-{h['id']:02d}-{week_start}",
                        "",
                    ))
                    pool_count += 1

            if (year, month) != (2025, 3):
                conn.execute("""
                    INSERT INTO monthly_status (hotel_id, year, month, status)
                    VALUES (?,?,?,?)
                """, (h["id"], year, month, "checked"))

    # A handful of sample petty cash vouchers so that page isn't empty
    voucher_count = 0
    for i in range(6):
        category = random.choice(PETTY_CASH_CATEGORIES)
        amount = round(random.uniform(10, 150), 2)
        voucher_date = f"2025-{random.randint(1,3):02d}-{random.randint(1,27):02d}"
        cur = conn.execute("""
            INSERT INTO petty_cash_vouchers
              (voucher_date, required_for, category, passed_by, signature, notes, total_amount)
            VALUES (?,?,?,?,?,?,?)
        """, (
            voucher_date, f"Sample expense {i + 1}", category,
            "Demo Manager", "", "Sample data \u2014 not a real transaction", amount,
        ))
        conn.execute("""
            INSERT INTO petty_cash_items (voucher_id, description, amount_gbp, gross, vat)
            VALUES (?,?,?,?,?)
        """, (cur.lastrowid, f"{category} item", amount, amount, 0))
        voucher_count += 1

    conn.commit()
    conn.close()

    if verbose:
        print(f"Created {result_count} weekly income entries, {pool_count} pool stock "
              f"entries, and {voucher_count} petty cash vouchers across {len(months)} months.")
    return {
        "hotels": len(hotels),
        "daily_results": result_count,
        "pool_stock": pool_count,
        "petty_cash_vouchers": voucher_count,
    }


if __name__ == "__main__":
    seed_demo_data()
    print("\nDone. Start the server: python app.py")
