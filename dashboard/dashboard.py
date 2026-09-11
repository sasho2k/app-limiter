import os
import tkinter as tk
from tkinter import ttk
from datetime import date
import db

class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("App Limiter Dashboard")
        self.geometry("1200x800")

        db_path = os.path.join(os.getcwd(), "app_limiter.db")
        self.conn = db.get_connection_db(db_path)

        columns = ("app", "running", "focused", "limit")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, label in zip(columns, ["App", "Running (min)", "Focused (min)", "Limit (min)"]):
            self.tree.heading(col, text=label)
        self.tree.pack(fill="both", expand=True)

        ttk.Button(self, text="Refresh", command=self.refresh).pack(pady=5)
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        today = date.today().isoformat()
        for app in db.get_all_apps_db(self.conn):
            name = app["process_name"]
            running = db.get_today_usage_db(self.conn, name, today) / 60
            focused = db.get_today_focused_usage_db(self.conn, name, today) / 60
            limit = app["daily_limit_minutes"] or "-"
            self.tree.insert("", "end", values=(name, f"{running:.1f}", f"{focused:.1f}", limit))

if __name__ == "__main__":
    Dashboard().mainloop()
