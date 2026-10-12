"""Set the public website URL before generating the Xcode project."""
import argparse
import plistlib
from pathlib import Path
from urllib.parse import urlsplit

parser = argparse.ArgumentParser()
parser.add_argument('website', help='Your live HTTPS Render website URL')
args = parser.parse_args()
url = args.website.strip().rstrip('/')
try:
    parts = urlsplit(url)
    valid = parts.scheme == 'https' and bool(parts.hostname) and not parts.username and not parts.password and parts.path in ('', '/') and not parts.query and not parts.fragment and not any(c.isspace() for c in url)
except ValueError:
    valid = False
if not valid:
    parser.error('Use your public HTTPS website origin, without credentials, a path, query, or fragment.')
path = Path(__file__).parent / 'PipeTime' / 'ClientConfig.plist'
path.write_bytes(plistlib.dumps({'WebsiteURL': url}))
print('Website configured. On a Mac, run xcodegen generate in mobile-ios.')
