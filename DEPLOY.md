# Render deployment

This checkout has not been published to GitHub or deployed to Render.

Create a Python Web Service connected to `Pipetimeplumbing/pipetimeplumbing` after the code is committed and pushed.

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --access-logfile -`
- Health check path: `/health`
- Persistent disk mount path: `/var/data`
- Environment variable: `DATABASE_PATH=/var/data/requests.sqlite`
- Optional environment variable: `PAYMENT_URL` — overrides the business-provided Stripe link `https://buy.stripe.com/28E3cngMAcbh9vY5WEgEg02`. Do not use a password or API key. The Make a payment button opens the configured page; an explicitly empty or invalid override shows billing assistance with the business phone number. No card information is collected or stored by this app, and no invoice amount or payment status is inferred. Payment confirmations and reconciliation are handled in Stripe; this app does not mark invoices as paid.

A persistent disk requires a compatible paid Render service. Check current pricing before creating it. Without a disk, the local SQLite database is temporary and is not suitable for real customer requests. For a free deployment, use an external persistent database instead; that integration is not implemented here.

Client registration, hashed passwords, 24-hour server-side sessions, and account message history are implemented in `app.py`. HTTPS on Render sets secure session cookies automatically. Client accounts, sessions, and messages all require the persistent database above. No secret key environment variable is needed for these opaque database-backed sessions. Email verification and password reset are not implemented. The legacy `python server.py` development server does not support client accounts; use Gunicorn for the full app.

The production entry point is `app.py`; `server.py` remains the local development server. Do not collect real customer requests until staff access, notifications, abuse protection, and privacy terms are implemented. Never add credentials to this repository.
