# Linux Domain Controller Web Manager

A web application for managing a Samba Active Directory domain controller running on Linux. Provides a browser-based interface for common AD administration tasks.

## Features

- **User Management** — Create, delete, enable/disable AD users. Reset passwords and set account expiry.
- **Group Management** — Create and delete groups. Add/remove members from groups.
- **Computer Management** — Pre-stage computer accounts for domain joining. View and remove domain-joined machines.
- **Dashboard** — Overview of domain stats (user/group/computer counts, domain functional level).
- **Authentication** — Logs in against Samba AD itself — no separate user database.

## Requirements

- Linux server running **Samba as an Active Directory Domain Controller**
- Python 3.9+
- `samba-tool` available on `PATH` (installed with Samba AD DC)

## Quick Start

```bash
# Clone the repo
git clone <repo-url> /opt/dc-manager
cd /opt/dc-manager

# Create virtualenv and install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your domain settings:
#   SAMBA_REALM=YOUR.DOMAIN
#   SAMBA_DOMAIN=YOUR
#   SAMBA_DC_HOST=localhost
#   SECRET_KEY=<random-string>

# Run (development)
python run.py

# Run (production with gunicorn)
gunicorn --config gunicorn.conf.py wsgi:application
```

The app listens on `http://0.0.0.0:5000` by default. Log in with an AD administrator account.

## Production Deployment

A systemd service file is included:

```bash
cp dc-manager.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now dc-manager
```

For HTTPS, place a reverse proxy (nginx/caddy) in front of gunicorn.

## Configuration

All settings are in `.env` (see `.env.example`):

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Flask session secret | Random |
| `SAMBA_REALM` | AD realm (e.g. `CORP.LOCAL`) | `EXAMPLE.LOCAL` |
| `SAMBA_DOMAIN` | NetBIOS domain name | `EXAMPLE` |
| `SAMBA_DC_HOST` | DC hostname/IP | `localhost` |
| `SAMBA_ADMIN_USER` | Default admin username | `Administrator` |
| `SAMBA_TOOL_PATH` | Path to samba-tool binary | `/usr/bin/samba-tool` |
| `FLASK_ENV` | `development` or `production` | `production` |

## Project Structure

```
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── forms.py             # WTForms definitions
│   ├── models.py            # Flask-Login user model
│   ├── routes/
│   │   ├── auth.py          # Login/logout
│   │   ├── dashboard.py     # Home dashboard
│   │   ├── users.py         # User CRUD
│   │   ├── groups.py        # Group management
│   │   └── computers.py     # Computer accounts
│   ├── services/
│   │   └── samba.py         # samba-tool wrapper
│   ├── static/css/style.css
│   └── templates/           # Jinja2 templates
├── config/settings.py       # App configuration
├── tests/                   # pytest test suite
├── run.py                   # Development entry point
├── wsgi.py                  # Production WSGI entry
├── gunicorn.conf.py         # Gunicorn config
└── dc-manager.service       # systemd unit file
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```
