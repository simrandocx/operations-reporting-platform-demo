# Roadmap

## Current Status

Working prototype. The platform is not yet deployed to production.

## Known Limitations

- SQLite is suitable for single-user use only.
- No authentication yet.
- The app is local-only unless deployed.
- OCR may struggle with multi-column photographed packing lists.
- Historical Excel import is not yet completed.
- No full audit log table yet.

## Planned Improvements

- [ ] Import historical data from existing spreadsheets
- [ ] Add user login and authentication
- [ ] Add role-based access for manager/admin users
- [ ] Deploy to Railway, Render, or another hosting service
- [ ] Add OneDrive or cloud backup integration
- [ ] Improve pool stock photo scanning with a vision model
- [ ] Add price list tracking per customer
- [ ] Add PDF exports
- [ ] Add full audit logs for important edits
- [ ] Migrate from SQLite to PostgreSQL for multi-user deployment
