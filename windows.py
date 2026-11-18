import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from config import (
    VERSION, CLR_BG, CLR_CARD, CLR_GREEN, CLR_CYAN, CLR_RED,
    CLR_PURPLE, CLR_YELLOW, CLR_DARK_GREEN
)
from adb_service import get_subprocess_flags, get_adb_path

class LogcatWindow(ctk.CTkToplevel):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.title(f"📄 Real-Time ADB Logcat Viewer — {VERSION}")
        self.geometry("850x580")
        self.configure(fg_color=CLR_BG)
        self.is_logging = False
        self.log_thread = None

        top_frame = ctk.CTkFrame(self, fg_color=CLR_CARD, corner_radius=8)
        top_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top_frame, text="Фильтр:", text_color=CLR_GREEN, font=("Arial", 12, "bold")).pack(side="left", padx=8)
        self.entry_filter = ctk.CTkEntry(top_frame, placeholder_text="Error, Warning, ActivityManager...", width=220)
        self.entry_filter.pack(side="left", padx=5)

        self.btn_start = ctk.CTkButton(top_frame, text="▶ Старт", width=80, command=self.start_logging, fg_color=CLR_DARK_GREEN, text_color=CLR_GREEN)
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = ctk.CTkButton(top_frame, text="⏹ Стоп", width=80, command=self.stop_logging, fg_color="#3A0A0A", text_color=CLR_RED)
        self.btn_stop.pack(side="left", padx=5)

        self.btn_clear = ctk.CTkButton(top_frame, text="🧹 Очистить", width=90, command=self.clear_log, fg_color="#181825", text_color=CLR_CYAN)
        self.btn_clear.pack(side="left", padx=5)

        self.txt_log = ctk.CTkTextbox(self, font=("Consolas", 10), fg_color="#020304", text_color="#00FF88", border_color="#112215", border_width=1)
        self.txt_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def start_logging(self):
        if not self.app.device_id:
            messagebox.showwarning("Ошибка", "Устройство не подключено!")
            return
        if not self.is_logging:
            self.is_logging = True
            self.log_thread = threading.Thread(target=self._log_worker, daemon=True)
            self.log_thread.start()

    def stop_logging(self):
        self.is_logging = False

    def clear_log(self):
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")

    def _log_worker(self):
        adb_bin = get_adb_path()
        cmd = f'"{adb_bin}" -s {self.app.device_id} logcat'
        flags = get_subprocess_flags()
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="ignore", env=os.environ, creationflags=flags)

        while self.is_logging and proc.poll() is None:
            line = proc.stdout.readline()
            if line:
                filter_text = self.entry_filter.get().strip().lower()
                if not filter_text or filter_text in line.lower():
                    self.txt_log.configure(state="normal")
                    self.txt_log.insert("end", line)
                    self.txt_log.see("end")
                    self.txt_log.configure(state="disabled")
            time.sleep(0.01)

        proc.terminate()

    def destroy(self):
        self.stop_logging()
        super().destroy()


class AppInspectorWindow(ctk.CTkToplevel):
    def __init__(self, master, app_instance, package_name):
        super().__init__(master)
        self.app = app_instance
        self.package_name = package_name
        self.title(f"🔍 Инспектор: {package_name}")
        self.geometry("650x520")
        self.configure(fg_color=CLR_BG)

        ctk.CTkLabel(self, text="📱 ИНФОРМАЦИЯ О ПАКЕТЕ", font=("Arial", 16, "bold"), text_color=CLR_CYAN).pack(pady=12)
        ctk.CTkLabel(self, text=package_name, font=("Consolas", 12, "bold"), text_color=CLR_GREEN).pack(pady=(0, 10))

        self.txt_info = ctk.CTkTextbox(self, font=("Consolas", 10), fg_color=CLR_CARD, text_color="#E0E0E0")
        self.txt_info.pack(fill="both", expand=True, padx=15, pady=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(btn_frame, text="Остановить (Force Stop)", command=self.force_stop, fg_color="#3A1A0A", text_color=CLR_YELLOW).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="Очистить Данные (Clear Data)", command=self.clear_data, fg_color="#3A0A0A", text_color=CLR_RED).pack(side="left", padx=5, expand=True, fill="x")

        self.load_details()

    def load_details(self):
        path_raw = self.app.run_adb(f"shell pm path {self.package_name}")
        dump_raw = self.app.run_adb(f"shell dumpsys package {self.package_name}")

        version = "Неизвестно"
        uid = "Неизвестно"
        for line in dump_raw.splitlines():
            if "versionName" in line:
                version = line.split("=")[-1].strip()
            if "userId=" in line:
                uid = line.split("userId=")[-1].strip().split()[0]

        info_text = f"""==================================================
ДЕТАЛИ ПАКЕТА: {self.package_name}
==================================================
• Версия приложения: {version}
• Идентификатор UID: {uid}
• Путь к APK: {path_raw.replace('package:', '').strip()}

==================================================
ВЫДЕРЖКА РАЗРЕШЕНИЙ (PERMISSIONS):
==================================================
"""
        perms = [line.strip() for line in dump_raw.splitlines() if "android.permission." in line]
        info_text += "\n".join(perms[:20]) if perms else "Разрешения не найдены."

        self.txt_info.insert("1.0", info_text)

    def force_stop(self):
        self.app.run_adb(f"shell am force-stop {self.package_name}")
        messagebox.showinfo("Готово", f"Приложение {self.package_name} остановлено.")

    def clear_data(self):
        if messagebox.askyesno("Подтверждение", f"Сбросить все данные и кэш для {self.package_name}?"):
            self.app.run_adb(f"shell pm clear {self.package_name}")
            messagebox.showinfo("Готово", f"Данные пакета {self.package_name} успешно сброшены.")


class FileManagerWindow(ctk.CTkToplevel):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance
        self.current_path = "/sdcard"
        self.title("📂 ADB File Explorer — /sdcard/")
        self.geometry("750x540")
        self.configure(fg_color=CLR_BG)

        top = ctk.CTkFrame(self, fg_color=CLR_CARD)
        top.pack(fill="x", padx=10, pady=10)

        self.lbl_path = ctk.CTkLabel(top, text=self.current_path, font=("Consolas", 11, "bold"), text_color=CLR_GREEN)
        self.lbl_path.pack(side="left", padx=10)

        ctk.CTkButton(top, text="⬆ Наверх", width=80, command=self.go_up, fg_color=CLR_DARK_GREEN, text_color=CLR_GREEN).pack(side="right", padx=5)

        self.file_listbox = tk.Listbox(self, bg="#030507", fg=CLR_CYAN, selectbackground=CLR_GREEN, selectforeground="#000", font=("Consolas", 10))
        self.file_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.file_listbox.bind("<Double-1>", self.on_double_click)

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(bottom, text="📥 Скачать на ПК (Pull)", command=self.pull_file, fg_color="#0A2030", text_color=CLR_CYAN).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(bottom, text="📤 Загрузить на Телефон (Push)", command=self.push_file, fg_color="#200A30", text_color=CLR_PURPLE).pack(side="left", padx=5, expand=True, fill="x")

        self.load_files()

    def load_files(self):
        self.lbl_path.configure(text=self.current_path)
        self.file_listbox.delete(0, tk.END)
        out = self.app.run_adb(f'shell "ls -F {self.current_path}"')
        if out:
            for item in sorted(out.splitlines()):
                self.file_listbox.insert(tk.END, item)

    def on_double_click(self, event):
        sel = self.file_listbox.curselection()
        if not sel:
            return
        item = self.file_listbox.get(sel[0])
        if item.endswith("/"):
            folder_name = item.rstrip("/")
            self.current_path = f"{self.current_path}/{folder_name}".replace("//", "/")
            self.load_files()

    def go_up(self):
        if self.current_path != "/sdcard" and self.current_path != "/":
            self.current_path = os.path.dirname(self.current_path)
            if not self.current_path:
                self.current_path = "/sdcard"
            self.load_files()

    def pull_file(self):
        sel = self.file_listbox.curselection()
        if not sel:
            return
        item = self.file_listbox.get(sel[0]).rstrip("/")
        remote_file = f"{self.current_path}/{item}"

        save_dir = filedialog.askdirectory(title="Выберите папку для сохранения на ПК")
        if save_dir:
            dest = os.path.join(save_dir, item)
            self.app.run_adb(f'pull "{remote_file}" "{dest}"')
            messagebox.showinfo("Успех", f"Файл сохранен: {dest}")

    def push_file(self):
        local_file = filedialog.askopenfilename(title="Выберите файл для загрузки на телефон")
        if local_file:
            filename = os.path.basename(local_file)
            remote_dest = f"{self.current_path}/{filename}"
            self.app.run_adb(f'push "{local_file}" "{remote_dest}"')
            messagebox.showinfo("Успех", f"Файл загружен в: {remote_dest}")
            self.load_files()
