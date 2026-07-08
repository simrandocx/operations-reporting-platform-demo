# Database Schema

The platform uses SQLite for the current local prototype.

## Tables

| Table | Purpose |
|---|---|
| `hotels` | Stores customers, including hotels and outside contracts |
| `daily_results` | Stores weekly income entries per customer |
| `monthly_status` | Stores finalisation status per customer per month |
| `pool_stock` | Stores daily linen movement entries |
| `scanned_packing_lists` | Stores OCR scan metadata and status |
| `petty_cash_vouchers` | Stores petty cash voucher headers |
| `petty_cash_items` | Stores line items within each voucher |
| `price_list` | Reserved for future customer pricing data |

## Notes

- SQLite is suitable for the current single-user prototype.
- If the platform becomes multi-user or cloud-hosted, PostgreSQL should replace SQLite.
- Backups should copy the full `.db` file rather than only exporting CSV or JSON files.
- Monthly finalisation should protect already-approved results from casual edits.
