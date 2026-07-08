# Architecture

## Overview

The Laundry Manager Dashboard is a local-first full-stack application.

```text
React frontend
      ↓
Flask API
      ↓
SQLite database
      ↓
Excel export / database backup
```

## Backend

The backend is built with Flask. It exposes routes for customers, income entries, pool stock, petty cash, analytics, exports, and backups.

The current design keeps the backend simple by using explicit SQL through Python's built-in SQLite tooling rather than an ORM.

## Frontend

The frontend is a single React page loaded through a browser. The current prototype avoids a Node build step by using React through a CDN.

## Design Decisions

### Raw SQLite instead of ORM

Raw SQL keeps the dependency count low and makes the queries easier to inspect for a small internal system.

### Weekly income entry

The original idea was daily income entry, but weekly entry better matches the actual reporting workflow and reduces unnecessary manual input.

### Template-based pool stock

Each customer can have a predefined linen item list in the same order as their physical packing list. This makes entry faster and improves scan matching.

### Finalisation with correction notes

Once a month is marked as finalised, future edits should require a written correction note. This provides a simple audit trail without building a full audit log system immediately.

### Full database backups

Backups should copy the full SQLite file. This makes recovery easier because the backup can be restored directly without importing separate files.
