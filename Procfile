# --workers 1 is intentional: visitor "sandboxes" (see backend/db.py) live
# in that one process's memory. Multiple workers would each keep their own
# separate set of sandboxes, so a visitor could randomly land on a
# different worker (and a different, empty sandbox) between requests.
web: gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT --workers 1
