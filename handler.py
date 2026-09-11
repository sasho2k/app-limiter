from monitor import *
from db import *
import os
from datetime import date

# main
def main(debug):
    # DEBUG MODE:
    debug = False

    # List of apps that won't be tracked
    excluded_apps = ["ApplicationFrameHost.exe", "explorer.exe", "TextInputHost.exe", "Taskmgr.exe"]

    # Path of current working directory + file name
    db_path = os.path.join(os.getcwd(), "app_limiter.db")
    if debug:
        print("db_path: ", db_path)

    # Establish a connection
    conn = get_connection_db(db_path)
    if debug:
        print(conn)

    # Init db; Will not overwrite tables if they exist
    init_db(conn)

    sleep_time = 3
    last_tick = time.time()

    while True:
        time.sleep(sleep_time)
        if debug:
            print("slept for ", sleep_time)

        # Actual time since the last tick, capped so a system sleep/hibernate
        # gap doesn't get credited as usage
        now = time.time()
        elapsed = min(now - last_tick, sleep_time * 3)
        last_tick = now

        # Today
        today = date.today().isoformat()
        if debug:
            print("today: ", today)

        # "Running" tracking every visible app, focused or not
        apps = get_foreground_apps()
        for app in apps:
            process_name = app.name()
            if process_name in excluded_apps:
                continue
            if app.status() != "running":
                continue
            if debug:
                print("process name: ", process_name)

            existing_app = get_app_db(conn, process_name)
            if existing_app is None:
                add_app_db(conn, process_name)
                if debug:
                    print("added app: ", process_name)

            add_daily_usage_result = add_daily_usage_db(conn, process_name, today, seconds=elapsed)
            if debug: 
                print("add daily usage: ", add_daily_usage_result, process_name, today, elapsed)

        # "Focused" tracking only the one active window
        focused_process_name = get_focused_window()
        if focused_process_name and focused_process_name not in excluded_apps:
            if get_app_db(conn, focused_process_name):
                add_focused_usage_result = add_focused_usage_db(conn, focused_process_name, today, seconds=elapsed)
                if debug:
                    print("add focused usage: ", add_focused_usage_result, focused_process_name, today, elapsed)



# helper functions for now:
# will go into separate file soon


# Print db details and try getting data from all 3 tables
def db_pull_data_test():
    db_path = os.path.join(os.getcwd(), "app_limiter.db")
    print("db_path: ", db_path)

    # Establish a connection
    conn = get_connection_db(db_path)
    print(conn)

    today = date.today().isoformat()
    for app in get_all_apps_db(conn):
        print(app)
        print("usage: ", get_today_usage_db(conn, app['process_name'], today))
        print("focused usage: ", get_today_focused_usage_db(conn, app['process_name'], today))