# Pipe Time customer app

Run with Python 3.12 or newer: `python server.py` from this directory. Open port 3000 in your development preview. No package installation is required.

The responsive app supports appointment requests and customer messages. Both are persisted in `data/requests.sqlite`; it is not a live chat or a confirmed calendar booking. The server exposes no customer-data read endpoint. Review requests locally with SQLite or Python, and follow up by phone.

Before public launch, add an authenticated staff inbox, notifications, scheduling availability, HTTPS, abuse protection, privacy policy, and database backups. The current development server is not a production server. Uploaded logo integration remains pending: the original logo file was not available in the checkout, so the app uses a typographic brand mark. External Google Fonts are optional; local fallback fonts work offline.
