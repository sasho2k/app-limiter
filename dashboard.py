import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import date
from tkcalendar import DateEntry
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import db

class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("App Limiter Dashboard")
        self.geometry("1200x800")

        db_path = Path(__file__).resolve().parent / "app_limiter.db"
        self.conn = db.get_connection_db(db_path)

        controls = ttk.Frame(self)
        controls.pack(fill="x", padx=10, pady=10)

        earliest_date_str = db.get_earliest_usage_date_db(self.conn)
        mindate = date.fromisoformat(earliest_date_str) if earliest_date_str else None

        ttk.Label(controls, text="Date:").pack(side="left")
        self.date_picker = DateEntry(
            controls, date_pattern="yyyy-mm-dd", maxdate=date.today(), mindate=mindate
        )
        self.date_picker.pack(side="left", padx=5)
        self.date_picker.bind("<<DateEntrySelected>>", lambda _: self.refresh())

        ttk.Button(controls, text="Refresh", command=self.refresh).pack(side="left", padx=5)
        ttk.Button(controls, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=5)

        columns = ("app", "running", "focused", "limit")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)
        for col, label in zip(columns, ["App", "Running (min)", "Focused (min)", "Limit (min)"]):
            self.tree.heading(col, text=label)
        self.tree.pack(fill="x", padx=10, pady=(0, 10))

        self.figure = Figure(figsize=(11, 5))
        self.bar_ax = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.refresh()

    def refresh(self):
        selected_date = self.date_picker.get_date().isoformat()
        self._refresh_table(selected_date)
        self._refresh_bar_chart(selected_date)
        self.canvas.draw()

    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            return

        process_name = self.tree.item(selection[0], "values")[0]
        if not messagebox.askyesno(
            "Delete app",
            f"Delete '{process_name}' and its usage history?\nIt will also stop being tracked going forward.",
        ):
            return

        db.delete_app_db(self.conn, process_name)
        self.refresh()

    def _refresh_table(self, selected_date):
        self.tree.delete(*self.tree.get_children())
        for app in db.get_all_apps_db(self.conn):
            name = app["process_name"]
            running = db.get_today_usage_db(self.conn, name, selected_date) / 60
            focused = db.get_today_focused_usage_db(self.conn, name, selected_date) / 60
            limit = app["daily_limit_minutes"] or "-"
            self.tree.insert("", "end", values=(name, f"{running:.1f}", f"{focused:.1f}", limit))

    def _refresh_bar_chart(self, selected_date):
        self.bar_ax.clear()

        names, running_vals, focused_vals = [], [], []
        for app in db.get_all_apps_db(self.conn):
            name = app["process_name"]
            names.append(name)
            running_vals.append(db.get_today_usage_db(self.conn, name, selected_date) / 60)
            focused_vals.append(db.get_today_focused_usage_db(self.conn, name, selected_date) / 60)

        self.bar_ax.set_title(f"Usage on {selected_date}")
        if names:
            x = range(len(names))
            width = 0.35
            self.bar_ax.bar([i - width / 2 for i in x], running_vals, width, label="Running")
            self.bar_ax.bar([i + width / 2 for i in x], focused_vals, width, label="Focused")
            self.bar_ax.set_xticks(list(x))
            self.bar_ax.set_xticklabels(names, rotation=30, ha="right")
            self.bar_ax.set_ylabel("Minutes")
            self.bar_ax.legend()
        else:
            self.bar_ax.text(0.5, 0.5, "No apps tracked yet", ha="center", va="center")

        self.figure.tight_layout()

if __name__ == "__main__":
    Dashboard().mainloop()
