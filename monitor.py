import psutil
import time
import win32gui
import win32process

# Try to get the process using the full .exe name in the system
def get_process(process_name):
    for process in psutil.process_iter(['pid', 'name', 'username']):
        if process.name() == process_name:
            return process

        

# get the seconds, minutes, and hours the process has been running FROM THE SYSTEM
def get_process_time(process):
    time_elapsed = round(time.time() - process.create_time(), 2)

    seconds = round(time_elapsed, 2)
    minutes = round(time_elapsed / 60, 2)
    hours = round(time_elapsed / 60 / 60, 2)

    return [seconds, minutes, hours]



# Kill the process
def kill_process(process):
    try: 
        process.kill()
    except psutil.NoSuchProcess:
        pass



# Get the name of the active foreground window, return "" if there is no window
def get_focused_window():
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return ""

    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return ""

# Get the apps that are in the foreground and return them as psutil objs
# Won't recognized windows that are background processes
def get_foreground_apps():
    apps = {}

    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        if not win32gui.GetWindowText(hwnd):
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            apps[pid] = psutil.Process(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    win32gui.EnumWindows(enum_handler, None)
    return list(apps.values())