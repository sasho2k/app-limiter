import psutil
import time

for proc in psutil.process_iter(['pid', 'name', 'username']):
    if proc.name() == "deadlock.exe":
        print(proc.name())

        time_elapsed = round(time.time() - proc.create_time(), 2)

        print("seconds: " + str(time_elapsed))
        print("minutes: " + str(time_elapsed / 60))
        print("hours: " + str(time_elapsed / 60 / 60))