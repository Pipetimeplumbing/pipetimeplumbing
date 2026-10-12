# Pipe Time customer app

An iPhone/iPad SwiftUI source package is available in `mobile-ios/`, configured for `https://pipetimeplumbing.onrender.com`. See `mobile-ios/README.md` for Mac build, signing, and App Store prerequisites. It has not been compiled or published. Client account deletion is now supported from the account page.

Run with Python 3.12 or newer from this directory: create a virtual environment, install `requirements.txt`, and run `gunicorn app:app --bind 0.0.0.0:3000`. Open port 3000 in your development preview. The legacy `server.py` supports forms only; use `app.py` for client accounts.

The `/login` client page supports registration, sign-in, sign-out, and private message history for messages sent while authenticated. Passwords use scrypt hashing; sessions expire after 24 hours. These accounts are separate from Housecall Pro. Email verification and password reset remain unimplemented. Persistent storage is required to retain accounts across deployments; see `DEPLOY.md`.

Booking buttons open the supplied Housecall Pro Online Booking widget. Configure services, available hours, scheduling rules, and confirmation behavior in Housecall Pro. Availability is supplied by that provider, not the local app. If its script is blocked or unavailable, customers see a retry message and phone number. Live provider availability has not been verified from this workspace because outbound access to its domain was denied.

Customer messages are persisted in `data/requests.sqlite`; messaging is a callback request, not live chat. The server exposes no customer-data read endpoint. Review messages locally with SQLite or Python and follow up by phone. Legacy appointment API support remains for existing local requests; the user interface now books through Housecall Pro.

Before public launch, add an authenticated staff inbox, notifications, scheduling availability, HTTPS, abuse protection, privacy policy, and database backups. The current development server is not a production server. Uploaded logo integration remains pending: the original logo file was not available in the checkout, so the app uses a typographic brand mark. External Google Fonts are optional; local fallback fonts work offline.
