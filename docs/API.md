# API Documentation

This document lists the planned and implemented API routes for the Laundry Manager Dashboard.

## Customers

| Method | Path | Description |
|---|---|---|
| GET | `/hotels` | List all customers |
| POST | `/hotels` | Create a customer |
| PATCH | `/hotels/<id>` | Update a customer |
| DELETE | `/hotels/<id>` | Delete a customer |

## Income

| Method | Path | Description |
|---|---|---|
| GET | `/daily-results` | List weekly income entries |
| POST | `/daily-results` | Create or update a weekly income entry |
| DELETE | `/daily-results/<id>` | Delete an income entry |
| GET | `/weekly-schedule/<year>/<month>` | Get generated week ranges for a month |
| GET | `/monthly-results` | Rolled-up monthly totals per customer |
| GET | `/monthly-results/summary/<year>/<month>` | Monthly summary across all customers |
| GET | `/monthly-results/comparison/<year>/<month>` | Month-on-month comparison |
| GET | `/monthly-status/<year>/<month>` | Finalisation status for all customers |
| POST | `/monthly-status` | Set or update a customer's monthly status |

## Pool Stock

| Method | Path | Description |
|---|---|---|
| GET | `/pool-stock` | List pool stock entries with filters |
| POST | `/pool-stock` | Create a pool stock entry |
| PATCH | `/pool-stock/<id>` | Update a pool stock entry |
| DELETE | `/pool-stock/<id>` | Delete a pool stock entry |
| GET | `/pool-stock/summary/<year>/<month>` | Summary by customer and item |
| POST | `/pool-stock/scan` | Upload and OCR a packing list photo |
| GET | `/pool-stock/scan/<id>/image` | Retrieve a scanned image |
| POST | `/pool-stock/scan/<id>/confirm` | Confirm OCR results and save entries |
| POST | `/pool-stock/scan/<id>/discard` | Discard a scan |
| GET | `/pool-stock/scans` | List recent scans |

## Analytics

| Method | Path | Description |
|---|---|---|
| GET | `/analytics/ranking/<year>/<month>` | Customer revenue ranking |
| GET | `/analytics/checks/<year>/<month>` | Data quality checks |
| GET | `/compare` | Flexible comparison endpoint |

## Petty Cash

| Method | Path | Description |
|---|---|---|
| GET | `/petty-cash/vouchers` | List vouchers |
| POST | `/petty-cash/vouchers` | Create a voucher |
| PATCH | `/petty-cash/vouchers/<id>` | Edit a voucher |
| DELETE | `/petty-cash/vouchers/<id>` | Delete a voucher |
| GET | `/petty-cash/breakdown/<year>/<month>` | Monthly breakdown table |
| GET | `/petty-cash/export/<year>/<month>` | Download breakdown as Excel |

## Exports and Backup

| Method | Path | Description |
|---|---|---|
| GET | `/exports/monthly-results` | Monthly results Excel export |
| GET | `/exports/pool-stock` | Pool stock Excel export |
| GET | `/exports/ranking` | Performance ranking Excel export |
| POST | `/backup/run` | Save a timestamped database backup |
| GET | `/backup/history` | List existing backups |

## Frontend

| Method | Path | Description |
|---|---|---|
| GET | `/app` | Serve the React frontend |
