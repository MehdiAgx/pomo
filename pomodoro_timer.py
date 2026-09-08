"""
Pomodoro Timer - Windows Desktop Application
A simple, distraction-free Pomodoro technique timer built with Tkinter.

Run with:  python pomodoro_timer.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

try:
    import winsound  # Windows-only sound alert
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("400x560")
        self.root.resizable(False, False)
        self.root.configure(bg="#2b2b2b")

        # Durations in minutes (defaults)
        self.work_duration = 25
        self.short_break_duration = 5
        self.long_break_duration = 15
        self.sessions_before_long_break = 4

        self.current_session_type = "Work"
        self.sessions_completed = 0
        self.time_left = self.work_duration * 60
        self.is_running = False
        self.timer_job = None

        self.build_ui()

    # ---------------- UI construction ----------------

    def build_ui(self):
        title_label = tk.Label(
            self.root, text="Pomodoro Timer", font=("Segoe UI", 20, "bold"),
            bg="#2b2b2b", fg="#ff6b6b"
        )
        title_label.pack(pady=(20, 10))

        self.session_label = tk.Label(
            self.root, text="Work Session", font=("Segoe UI", 14),
            bg="#2b2b2b", fg="#ffffff"
        )
        self.session_label.pack(pady=(0, 10))

        self.timer_label = tk.Label(
            self.root, text=self.format_time(self.time_left),
            font=("Segoe UI", 48, "bold"), bg="#2b2b2b", fg="#4ecdc4"
        )
        self.timer_label.pack(pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TProgressbar", troughcolor="#3c3c3c",
                         background="#4ecdc4", thickness=10)
        self.progress = ttk.Progressbar(
            self.root, style="TProgressbar", length=300,
            maximum=self.work_duration * 60, value=self.time_left
        )
        self.progress.pack(pady=10)

        self.counter_label = tk.Label(
            self.root, text=f"Completed Sessions: {self.sessions_completed}",
            font=("Segoe UI", 11), bg="#2b2b2b", fg="#aaaaaa"
        )
        self.counter_label.pack(pady=(0, 20))

        btn_frame = tk.Frame(self.root, bg="#2b2b2b")
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(
            btn_frame, text="Start", width=10, font=("Segoe UI", 11, "bold"),
            bg="#4ecdc4", fg="#000000", relief="flat", command=self.start_timer
        )
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(
            btn_frame, text="Pause", width=10, font=("Segoe UI", 11, "bold"),
            bg="#ffd93d", fg="#000000", relief="flat", command=self.pause_timer
        )
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = tk.Button(
            btn_frame, text="Reset", width=10, font=("Segoe UI", 11, "bold"),
            bg="#ff6b6b", fg="#000000", relief="flat", command=self.reset_timer
        )
        self.reset_btn.grid(row=0, column=2, padx=5)

        self.skip_btn = tk.Button(
            self.root, text="Skip to Next Session", font=("Segoe UI", 10),
            bg="#3c3c3c", fg="#ffffff", relief="flat", command=self.skip_session
        )
        self.skip_btn.pack(pady=10)

        settings_frame = tk.LabelFrame(
            self.root, text="Settings (minutes)", font=("Segoe UI", 10),
            bg="#2b2b2b", fg="#ffffff", relief="flat"
        )
        settings_frame.pack(pady=10, padx=20, fill="x")

        self.work_var = tk.StringVar(value=str(self.work_duration))
        self.short_var = tk.StringVar(value=str(self.short_break_duration))
        self.long_var = tk.StringVar(value=str(self.long_break_duration))

        self.add_setting_row(settings_frame, "Work:", self.work_var, 0)
        self.add_setting_row(settings_frame, "Short Break:", self.short_var, 1)
        self.add_setting_row(settings_frame, "Long Break:", self.long_var, 2)

        apply_btn = tk.Button(
            settings_frame, text="Apply Settings", font=("Segoe UI", 9),
            bg="#4ecdc4", fg="#000000", relief="flat", command=self.apply_settings
        )
        apply_btn.grid(row=3, column=0, columnspan=2, pady=8)

    def add_setting_row(self, parent, label_text, var, row):
        tk.Label(
            parent, text=label_text, bg="#2b2b2b", fg="#ffffff", font=("Segoe UI", 9)
        ).grid(row=row, column=0, sticky="w", padx=10, pady=4)
        entry = tk.Entry(parent, textvariable=var, width=6, font=("Segoe UI", 9))
        entry.grid(row=row, column=1, sticky="w", padx=10, pady=4)

    # ---------------- Settings ----------------

    def apply_settings(self):
        try:
            work = int(self.work_var.get())
            short = int(self.short_var.get())
            long_ = int(self.long_var.get())
            if any(v <= 0 for v in (work, short, long_)):
                raise ValueError
            self.work_duration = work
            self.short_break_duration = short
            self.long_break_duration = long_
            messagebox.showinfo("Settings Applied", "New durations will apply on the next session.")
            if not self.is_running:
                self.reset_timer()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter positive whole numbers for durations.")

    # ---------------- Timer logic ----------------

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.run_timer()

    def pause_timer(self):
        self.is_running = False
        if self.timer_job:
            self.root.after_cancel(self.timer_job)

    def reset_timer(self):
        self.pause_timer()
        self.current_session_type = "Work"
        self.session_label.config(text="Work Session")
        self.time_left = self.work_duration * 60
        self.progress.config(maximum=self.time_left, value=self.time_left)
        self.timer_label.config(text=self.format_time(self.time_left), fg="#4ecdc4")

    def run_timer(self):
        if self.is_running and self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=self.format_time(self.time_left))
            self.progress.config(value=self.time_left)
            self.timer_job = self.root.after(1000, self.run_timer)
        elif self.is_running and self.time_left == 0:
            self.play_alert()
            self.advance_session()

    def advance_session(self):
        if self.current_session_type == "Work":
            self.sessions_completed += 1
            self.counter_label.config(text=f"Completed Sessions: {self.sessions_completed}")
            if self.sessions_completed % self.sessions_before_long_break == 0:
                self.current_session_type = "Long Break"
                self.session_label.config(text="Long Break")
                self.time_left = self.long_break_duration * 60
                self.timer_label.config(fg="#a29bfe")
            else:
                self.current_session_type = "Short Break"
                self.session_label.config(text="Short Break")
                self.time_left = self.short_break_duration * 60
                self.timer_label.config(fg="#ffd93d")
        else:
            self.current_session_type = "Work"
            self.session_label.config(text="Work Session")
            self.time_left = self.work_duration * 60
            self.timer_label.config(fg="#4ecdc4")

        self.progress.config(maximum=self.time_left, value=self.time_left)
        self.timer_label.config(text=self.format_time(self.time_left))
        self.run_timer()

    def skip_session(self):
        self.play_alert()
        self.advance_session()

    def play_alert(self):
        def beep():
            if HAS_WINSOUND:
                try:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass
            else:
                # Fallback for non-Windows systems (e.g. terminal bell)
                print("\a", end="", flush=True)
        threading.Thread(target=beep, daemon=True).start()


def main():
    root = tk.Tk()
    PomodoroTimer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
