# Pipe Time customer app

Run with Python 3.12 or newer: `python server.py` from this directory. Open port 3000 in your development preview. No package installation is required.

Booking buttons open the supplied Housecall Pro Online Booking widget. Configure services, available hours, scheduling rules, and confirmation behavior in Housecall Pro. Availability is supplied by that provider, not the local app. If its script is blocked or unavailable, customers see a retry message and phone number. Live provider availability has not been verified from this workspace because outbound access to its domain was denied.

Customer messages are persisted in `data/requests.sqlite`; messaging is a callback request, not live chat. The server exposes no customer-data read endpoint. Review messages locally with SQLite or Python and follow up by phone. Legacy appointment API support remains for existing local requests; the user interface now books through Housecall Pro.

Before public launch, add an authenticated staff inbox, notifications, scheduling availability, HTTPS, abuse protection, privacy policy, and database backups. The current development server is not a production server. Uploaded logo integration remains pending: the original logo file was not available in the checkout, so the app uses a typographic brand mark. External Google Fonts are optional; local fallback fonts work offline.
