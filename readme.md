# App Limiter

A Windows app usage tracker and limiter. Runs in the background, tracks how long each app has been running and in focus, and can automatically kill an app once it exceeds a daily time limit you set.

## Features

- Tracks running and focused time per app, per day
- Optional daily time limit per app (auto-kills the process once exceeded)
- Dashboard UI for reviewing usage history and managing tracked apps
- Excludes apps from tracking on request

## Requirements

- Windows
- Python 3.10+
- [`psutil`](https://pypi.org/project/psutil/)
- [`pywin32`](https://pypi.org/project/pywin32/)
- [`tkcalendar`](https://pypi.org/project/tkcalendar/)
- [`matplotlib`](https://pypi.org/project/matplotlib/)

## Usage

Start the tracker (runs continuously, tracking apps and enforcing limits):

```bash
python main.py
```

Open the dashboard to view usage and manage tracked apps:

```bash
python dashboard.py
```

## Project Structure

| File | Purpose |
| --- | --- |
| `main.py` | Entry point, starts the tracking loop |
| `handler.py` | Ties monitoring and the database together, contains the main tracking loop |
| `monitor.py` | Reads process/window info from Windows |
| `db.py` | SQLite persistence for apps, usage, and exclusions |
| `dashboard.py` | Tkinter dashboard for viewing usage and deleting/excluding apps |

## Data

Usage data is stored locally in `app_limiter.db` (SQLite), created automatically on first run.
