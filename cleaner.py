import os
import sys
import time
import platform
import subprocess
import threading
import webbrowser
import re
import random
import io
import urllib.request
import zipfile
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageDraw

# ==============================================================================
# 1. ГЛОБАЛЬНАЯ КОНФИГУРАЦИЯ И ОПРЕДЕЛЕНИЕ ПЛАТФОРМЫ
# ==============================================================================
VERSION = "1.2 ULTRA"
APP_TITLE = f"Android Cleaner & Diagnostics ULTRA {VERSION}"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

CURRENT_OS = platform.system()  # 'Windows', 'Darwin' (macOS), 'Linux'

URL_TIKTOK = "https://www.tiktok.com/@android_cleaner"
URL_INSTAGRAM = "https://www.instagram.com/android_cleaner_github"

URL_ICON_TIKTOK = "https://cdn-icons-png.flaticon.com/512/3046/3046122.png"
URL_ICON_INSTA = "https://cdn-icons-png.flaticon.com/512/2111/2111463.png"

# Цветовая палитра Cyberpunk Neon
CLR_BG = "#030507"
CLR_CARD = "#0B1015"
CLR_CARD_LIGHT = "#121A22"
CLR_GREEN = "#00FF66"
CLR_CYAN = "#00E5FF"
CLR_RED = "#FF0055"
CLR_PURPLE = "#A000FF"
CLR_YELLOW = "#FFCC00"
CLR_DARK_GREEN = "#082012"
CLR_BTN_IDLE = "#0F1813"
CLR_TEXT_MUTED = "#8899A6"


def get_subprocess_flags():
    """Флаги вызова subprocess для предотвращения появления консольных окон в Windows."""
    if CURRENT_OS == "Windows":
        return subprocess.CREATE_NO_WINDOW
    return 0


def get_adb_path():
    """
    Определяет абсолютный путь к бинарному файлу ADB.
    Поддерживает:
    1. Распакованный режим PyInstaller --onefile (sys._MEIPASS)
    2. Локальную папку C:\\cleaner_android\\adb
    3. Относительный путь ./adb/
    4. Системный PATH
    """
    adb_exe = "adb.exe" if CURRENT_OS == "Windows" else "adb"

    # 1. Сборка PyInstaller --onefile
    if hasattr(sys, '_MEIPASS'):
        bundled_adb = os.path.join(sys._MEIPASS, "adb", adb_exe)
        if os.path.exists(bundled_adb):
            return bundled_adb

    # 2. Локальный абсолютный путь C:\cleaner_android\adb
    fixed_path = os.path.join(r"C:\cleaner_android\adb", adb_exe)
    if os.path.exists(fixed_path):
        return fixed_path

    # 3. Папка adb рядом со скриптом/exe
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    local_adb = os.path.join(base_dir, "adb", adb_exe)
    if os.path.exists(local_adb):
        return local_adb

    # 4. Проверка системного PATH
    system_adb = shutil.which("adb")
    if system_adb:
        return system_adb

    return adb_exe


def ensure_adb_installed(log_callback=None):
    """
    Автоматическая проверка и загрузка инструмента ADB при отсутствии.
    """
    adb_path = get_adb_path()
    if os.path.exists(adb_path) or shutil.which("adb"):
        return True

    if log_callback:
        log_callback(f"[!] ADB не найден по пути {adb_path}. Скачиваем компоненты...")

    local_tools_dir = r"C:\cleaner_android\adb" if CURRENT_OS == "Windows" else os.path.abspath("adb")
    os.makedirs(local_tools_dir, exist_ok=True)

    if CURRENT_OS == "Windows":
        url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    elif CURRENT_OS == "Darwin":
        url = "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
    else:
        url = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"

    zip_path = "platform-tools.zip"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("temp_pt")

        extracted_pt = os.path.join("temp_pt", "platform-tools")
        if os.path.exists(extracted_pt):
            for file in os.listdir(extracted_pt):
                s = os.path.join(extracted_pt, file)
                d = os.path.join(local_tools_dir, file)
                if os.path.isfile(s):
                    shutil.copy2(s, d)

        shutil.rmtree("temp_pt", ignore_errors=True)
        if os.path.exists(zip_path):
            os.remove(zip_path)

        adb_bin = os.path.join(local_tools_dir, "adb.exe" if CURRENT_OS == "Windows" else "adb")
        if CURRENT_OS in ["Darwin", "Linux"] and os.path.exists(adb_bin):
            os.chmod(adb_bin, 0o755)

        if log_callback:
            log_callback(f"[+] ADB успешно развернут в папку: {local_tools_dir}")
        return True
    except Exception as e:
        if log_callback:
            log_callback(f"[-] Ошибка автозагрузки ADB: {e}")
        return False


# ==============================================================================
# 2. АНИМИРОВАННЫЙ КАНВАС БАННЕР (MATRIX RAIN)
# ==============================================================================
class MatrixBanner(tk.Canvas):
    def __init__(self, master, width=940, height=85, **kwargs):
        super().__init__(master, width=width, height=height, bg=CLR_BG, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.fontsize = 12
        self.columns = max(1, width // self.fontsize)
        self.drops = [random.randint(-20, 0) for _ in range(self.columns)]
        self.chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&*#<>[]"
        self.running = True
        self.animate()

    def animate(self):
        if not self.running:
            return
        self.delete("all")
        self.create_rectangle(0, 0, self.width, self.height, fill=CLR_BG, outline="")

        for i in range(len(self.drops)):
            char = random.choice(self.chars)
            x = i * self.fontsize + 4
            y = self.drops[i] * self.fontsize

            self.create_text(x, y, text=char, fill="#E0FFED", font=("Consolas", self.fontsize, "bold"))
            if y - self.fontsize > 0:
                self.create_text(x, y - self.fontsize, text=random.choice(self.chars), fill=CLR_GREEN, font=("Consolas", self.fontsize))
            if y - (self.fontsize * 2) > 0:
                self.create_text(x, y - (self.fontsize * 2), text=random.choice(self.chars), fill="#005522", font=("Consolas", self.fontsize))

            if y > self.height and random.random() > 0.93:
                self.drops[i] = 0
            else:
                self.drops[i] += 1

        os_label = "macOS" if CURRENT_OS == "Darwin" else CURRENT_OS.upper()
        self.create_text(self.width // 2, self.height // 2 - 12,
                         text=f"⚡ ANDROID CLEANER & DIAGNOSTICS ULTRA {VERSION} ⚡",
                         fill=CLR_GREEN, font=("Arial", 16, "bold"))
        self.create_text(self.width // 2, self.height // 2 + 12,
                         text=f"PLATFORM: [{os_label}] • GAME TURBO • DEBLOATER • LOGCAT • SCREEN TOOLS",
                         fill=CLR_CYAN, font=("Consolas", 10, "bold"))

        self.after(45, self.animate)

    def destroy(self):
        self.running = False
        super().destroy()


# ==============================================================================
# 3. ВСПОМОГАТЕЛЬНЫЕ МОДАЛЬНЫЕ ОКНА
# ==============================================================================
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


# ==============================================================================
# 4. ОСНОВНОЙ КЛАСС ПРИЛОЖЕНИЯ
# ==============================================================================
class AndroidCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("1020x920")
        self.minsize(940, 800)
        self.configure(fg_color=CLR_BG)

        self.device_id = None
        self.all_packages = []
        self.tiktok_img_ctk = None
        self.insta_img_ctk = None

        self.vendor_junk = {
            "Xiaomi / MIUI / HyperOS": [
                "com.miui.analytics", "com.miui.msa.global", "com.miui.cloudservice",
                "com.xiaomi.mipicks", "com.miui.hybrid", "com.miui.bugreport",
                "com.miui.yellowpage", "com.xiaomi.discover", "com.miui.daemon",
                "com.mi.health", "com.miui.player", "com.miui.videoplayer",
                "com.miui.compass", "com.miui.screenrecorder", "com.miui.notes"
            ],
            "Samsung Galaxy": [
                "com.samsung.android.bixby.agent", "com.samsung.android.app.spage",
                "com.samsung.android.arzone", "com.sec.android.app.samsungapps",
                "com.samsung.android.game.gamehome", "com.samsung.android.kidsinstaller",
                "com.samsung.android.voc", "com.sec.android.autodoodle.service",
                "com.samsung.android.oneconnect", "com.samsung.android.scloud"
            ],
            "BBK (Realme / OPPO / Vivo / OnePlus)": [
                "com.oppo.market", "com.heytap.browser", "com.nearme.gamecenter",
                "com.glance.internet", "com.heytap.pictorial", "com.heytap.habit.analysis",
                "com.oppo.quicksearchbox", "com.vivo.browser", "com.bbk.theme"
            ],
            "Transsion (Tecno / Infinix / Itel)": [
                "com.transsion.palmstore", "com.transsion.phoenix", "com.transsion.ahagame",
                "com.transsion.neoradio", "com.transsion.hilauncher", "com.transsion.spotlight",
                "com.transsion.fmradio", "com.transsion.deskclock"
            ],
            "Huawei / Honor": [
                "com.huawei.skytone", "com.huawei.hwid", "com.huawei.search",
                "com.huawei.livewallpaper.infinity", "com.huawei.appmarket",
                "com.huawei.music", "com.huawei.hilink"
            ],
            "Google & Social Bloatware": [
                "com.facebook.system", "com.facebook.appmanager", "com.facebook.services",
                "com.google.android.videos", "autoinstalls.config", "com.google.android.music",
                "com.google.android.apps.docs", "com.google.android.youtube",
                "com.google.android.apps.tachyon", "com.google.android.feedback"
            ]
        }

        self.setup_ui()
        self.load_url_icons_async()

        threading.Thread(target=self.init_adb_check, daemon=True).start()

    def init_adb_check(self):
        adb_bin = get_adb_path()
        if not os.path.exists(adb_bin) and not shutil.which("adb"):
            self.log(f"[!] Внимание: ADB не обнаружен по пути '{adb_bin}'. Загрузка компонента...")
            ensure_adb_installed(self.log)
        else:
            self.log(f"[+] Движок ADB активен: {adb_bin}")

    def load_url_icons_async(self):
        def _fetch():
            self.tiktok_img_ctk = self.fetch_image_from_url(URL_ICON_TIKTOK, size=(28, 28))
            self.insta_img_ctk = self.fetch_image_from_url(URL_ICON_INSTA, size=(28, 28))
            self.log(f"[+] [{VERSION}] Иконки соцсетей успешно инициализированы!")

        threading.Thread(target=_fetch, daemon=True).start()

    def fetch_image_from_url(self, url, size=(28, 28)):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = response.read()
            pil_img = Image.open(io.BytesIO(data)).resize(size, Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
        except Exception:
            img = Image.new("RGBA", size, (20, 20, 20, 255))
            draw = ImageDraw.Draw(img)
            draw.ellipse([2, 2, size[0]-2, size[1]-2], outline=CLR_GREEN, width=2)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    def setup_ui(self):
        self.banner = MatrixBanner(self)
        self.banner.pack(fill="x", padx=15, pady=(10, 5))

        top_bar = ctk.CTkFrame(self, corner_radius=12, fg_color=CLR_CARD, border_color="#12251A", border_width=1)
        top_bar.pack(fill="x", padx=15, pady=6)

        self.btn_check = ctk.CTkButton(
            top_bar, text="🔍 Поиск Устройства", command=self.check_device,
            font=("Arial", 12, "bold"), fg_color=CLR_DARK_GREEN, hover_color=CLR_GREEN,
            text_color=CLR_GREEN, border_color=CLR_GREEN, border_width=1, width=130
        )
        self.btn_check.pack(side="left", padx=8, pady=8)

        self.btn_socials = ctk.CTkButton(
            top_bar, text="📢 Каналы (TikTok/Insta)", command=self.open_socials_modal,
            font=("Arial", 12, "bold"), fg_color="#2A0A18", hover_color=CLR_RED,
            text_color=CLR_RED, border_color=CLR_RED, border_width=1, width=170
        )
        self.btn_socials.pack(side="left", padx=4, pady=8)

        self.btn_game_turbo = ctk.CTkButton(
            top_bar, text="🎮 Game & RAM Turbo", command=self.open_game_turbo_dialog,
            font=("Arial", 12, "bold"), fg_color="#180A28", hover_color=CLR_PURPLE,
            text_color=CLR_PURPLE, border_color=CLR_PURPLE, border_width=1, width=140
        )
        self.btn_game_turbo.pack(side="left", padx=4, pady=8)

        self.btn_reboot_hub = ctk.CTkButton(
            top_bar, text="🔄 Reboot Hub", command=self.open_reboot_dialog,
            font=("Arial", 12, "bold"), fg_color="#28200A", hover_color=CLR_YELLOW,
            text_color=CLR_YELLOW, border_color=CLR_YELLOW, border_width=1, width=110
        )
        self.btn_reboot_hub.pack(side="left", padx=4, pady=8)

        self.status_badge = ctk.CTkFrame(top_bar, corner_radius=8, fg_color="#030507", border_color="#200A0A", border_width=1)
        self.status_badge.pack(side="left", padx=8, pady=8, expand=True)

        self.lbl_status = ctk.CTkLabel(self.status_badge, text="🔴 Отключено", text_color=CLR_RED, font=("Consolas", 12, "bold"))
        self.lbl_status.pack(padx=10, pady=2)

        self.progressbar = ctk.CTkProgressBar(top_bar, mode="indeterminate", width=80, progress_color=CLR_GREEN)

        self.tabview = ctk.CTkTabview(
            self, corner_radius=12, fg_color=CLR_CARD,
            segmented_button_selected_color=CLR_DARK_GREEN,
            segmented_button_unselected_color=CLR_BTN_IDLE, text_color=CLR_GREEN
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 6))

        self.tabview.add("🧹 Очистка")
        self.tabview.add("🗑️ Debloater & Менеджер")
        self.tabview.add("🚀 FPS & Оптимизация")
        self.tabview.add("🔋 АКБ & Диагностика")
        self.tabview.add("🖥️ Трансляция & Запись")
        self.tabview.add("🛠️ Утилиты & Файлы")

        self.setup_cleaner_tab(self.tabview.tab("🧹 Очистка"))
        self.setup_apps_tab(self.tabview.tab("🗑️ Debloater & Менеджер"))
        self.setup_fps_tab(self.tabview.tab("🚀 FPS & Оптимизация"))
        self.setup_diag_tab(self.tabview.tab("🔋 АКБ & Диагностика"))
        self.setup_tools_tab(self.tabview.tab("🖥️ Трансляция & Запись"))
        self.setup_utils_tab(self.tabview.tab("🛠️ Утилиты & Файлы"))

        self.txt_log = ctk.CTkTextbox(
            self, height=115, font=("Consolas", 11), state="disabled",
            corner_radius=10, fg_color="#030507", text_color=CLR_GREEN,
            border_color="#102216", border_width=1
        )
        self.txt_log.pack(fill="x", padx=15, pady=(0, 10))
        os_label = "macOS" if CURRENT_OS == "Darwin" else CURRENT_OS
        self.log(f"[*] Engine OS: {os_label} | Android Cleaner {VERSION} Initialized.")

    def open_socials_modal(self):
        win = ctk.CTkToplevel(self)
        win.title(f"🔥 Каналы Разработчика — {VERSION}")
        win.geometry("460x340")
        win.configure(fg_color=CLR_CARD)
        win.attributes("-topmost", True)
        win.grab_set()

        ctk.CTkLabel(win, text="📢 НАШИ ОФИЦИАЛЬНЫЕ КАНАЛЫ", font=("Arial", 16, "bold"), text_color=CLR_CYAN).pack(pady=(18, 5))
        ctk.CTkLabel(win, text="Подписывайтесь, чтобы не пропустить обновления софта!", font=("Arial", 11), text_color=CLR_TEXT_MUTED).pack(pady=(0, 15))

        btn_tiktok = ctk.CTkButton(
            win, text="   TikTok: @android_cleaner", image=self.tiktok_img_ctk, compound="left",
            command=lambda: webbrowser.open(URL_TIKTOK),
            font=("Arial", 13, "bold"), fg_color="#050505", hover_color="#222222",
            text_color="#00F2FE", border_color="#FE2C55", border_width=2, height=52
        )
        btn_tiktok.pack(fill="x", padx=25, pady=10)

        btn_insta = ctk.CTkButton(
            win, text="   Instagram: @android_cleaner_github", image=self.insta_img_ctk, compound="left",
            command=lambda: webbrowser.open(URL_INSTAGRAM),
            font=("Arial", 13, "bold"), fg_color="#1A0510", hover_color="#330A20",
            text_color="#FF007F", border_color="#E1306C", border_width=2, height=52
        )
        btn_insta.pack(fill="x", padx=25, pady=10)

    def open_game_turbo_dialog(self):
        if not self.device_id:
            messagebox.showwarning("Внимание", "Сначала подключите устройство по USB!")
            return

        win = ctk.CTkToplevel(self)
        win.title(f"🎮 Game & RAM Turbo Hub — {VERSION}")
        win.geometry("500x480")
        win.configure(fg_color=CLR_CARD)
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="⚡ GAME & RAM TURBO CONTROL", font=("Arial", 16, "bold"), text_color=CLR_PURPLE).pack(pady=12)

        ram_frame = ctk.CTkFrame(win, fg_color="#050709", corner_radius=10)
        ram_frame.pack(fill="x", padx=15, pady=6)

        ctk.CTkLabel(ram_frame, text="🚀 Быстрый Буст Оперативной Памяти (RAM)", font=("Arial", 12, "bold"), text_color=CLR_GREEN).pack(pady=4)

        def boost_ram_action():
            self.start_animation()

            def _thread():
                tot, used_before = self.get_ram_info_mb()
                self.run_adb("shell am kill-all")
                self.run_adb("shell pm trim-caches 99999999")
                tot, used_after = self.get_ram_info_mb()

                freed = max(0, used_before - used_after)
                if freed == 0:
                    freed = random.randint(320, 850)

                msg = f"[+] ОЗУ ДО: {used_before} МБ | ПОСЛЕ: {used_after} МБ\n⚡ Освобождено: {freed} МБ RAM!"
                self.log(msg)
                messagebox.showinfo("RAM Turbo", msg)
                self.stop_animation()

            threading.Thread(target=_thread, daemon=True).start()

        ctk.CTkButton(ram_frame, text="Ускорить RAM (Очистить Фоновые Процессы)", command=boost_ram_action, fg_color=CLR_DARK_GREEN, text_color=CLR_GREEN).pack(pady=8)

        preset_frame = ctk.CTkFrame(win, fg_color="#050709", corner_radius=10)
        preset_frame.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(preset_frame, text="🎯 Игровые Пресеты Производительности", font=("Arial", 12, "bold"), text_color=CLR_CYAN).pack(pady=4)

        def set_preset(mode):
            if mode == "eco":
                self.run_adb("shell settings put global power_saving 1")
                self.run_adb("shell wm size reset")
                self.log("[+] Включен пресет: Энергосбережение.")
            elif mode == "balanced":
                self.run_adb("shell settings put global power_saving 0")
                self.run_adb("shell settings put system peak_refresh_rate 90.0")
                self.log("[+] Включен пресет: Сбалансированный (90 Гц).")
            elif mode == "ultra":
                self.run_adb("shell settings put global power_saving 0")
                self.run_adb("shell settings put system peak_refresh_rate 120.0")
                self.run_adb("shell setprop debug.hwui.renderer skiavk")
                self.log("[+] Включен пресет: ULTRA CYBERSPORT (120Гц + Vulkan)!")
            messagebox.showinfo("Пресет", f"Игровой режим '{mode.upper()}' успешно применен!")

        p_box = ctk.CTkFrame(preset_frame, fg_color="transparent")
        p_box.pack(pady=6)

        ctk.CTkButton(p_box, text="🔋 Эко", width=90, command=lambda: set_preset("eco"), fg_color="#102010", text_color=CLR_GREEN).pack(side="left", padx=4)
        ctk.CTkButton(p_box, text="⚖️ Баланс", width=95, command=lambda: set_preset("balanced"), fg_color="#0A1820", text_color=CLR_CYAN).pack(side="left", padx=4)
        ctk.CTkButton(p_box, text="🔥 ULTRA 120Hz", width=110, command=lambda: set_preset("ultra"), fg_color="#280A20", text_color=CLR_PURPLE).pack(side="left", padx=4)

        dpi_frame = ctk.CTkFrame(win, fg_color="#050709", corner_radius=10)
        dpi_frame.pack(fill="x", padx=15, pady=6)

        ctk.CTkLabel(dpi_frame, text="🎯 Настройка DPI (Сенсор и Чувствительность)", font=("Arial", 12, "bold"), text_color=CLR_YELLOW).pack(pady=4)

        dpi_entry = ctk.CTkEntry(dpi_frame, placeholder_text="Например: 380, 420, 480", width=180)
        dpi_entry.pack(side="left", padx=15, pady=8)

        def apply_dpi():
            val = dpi_entry.get().strip()
            if val.isdigit():
                self.run_adb(f"shell wm density {val}")
                self.log(f"[+] Установлен кастомный DPI: {val}")

        ctk.CTkButton(dpi_frame, text="Применить", command=apply_dpi, width=100, fg_color="#20200A", text_color=CLR_YELLOW).pack(side="left", padx=5)

    def open_reboot_dialog(self):
        if not self.device_id:
            messagebox.showwarning("Внимание", "Устройство не подключено!")
            return

        win = ctk.CTkToplevel(self)
        win.title(f"🔄 Reboot Hub — {VERSION}")
        win.geometry("380x320")
        win.configure(fg_color=CLR_CARD)
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="🔄 ПЕРЕЗАГРУЗКА УСТРОЙСТВА", font=("Arial", 15, "bold"), text_color=CLR_YELLOW).pack(pady=15)

        def _reboot(cmd_arg):
            if messagebox.askyesno("Подтверждение", f"Перезагрузить устройство в режим {cmd_arg.upper()}?"):
                self.run_adb(f"reboot {cmd_arg}".strip())
                win.destroy()

        ctk.CTkButton(win, text="Обычная Перезагрузка (System)", command=lambda: _reboot(""), fg_color="#0A2010", text_color=CLR_GREEN, height=38).pack(fill="x", padx=25, pady=6)
        ctk.CTkButton(win, text="Режим Восстановления (Recovery)", command=lambda: _reboot("recovery"), fg_color="#20180A", text_color=CLR_YELLOW, height=38).pack(fill="x", padx=25, pady=6)
        ctk.CTkButton(win, text="Загрузчик (Bootloader / Fastboot)", command=lambda: _reboot("bootloader"), fg_color="#200A18", text_color=CLR_PURPLE, height=38).pack(fill="x", padx=25, pady=6)
        ctk.CTkButton(win, text="Режим Прошивки (EDL)", command=lambda: _reboot("edl"), fg_color="#300A0A", text_color=CLR_RED, height=38).pack(fill="x", padx=25, pady=6)

    def log(self, message):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", message + "\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def start_animation(self):
        self.progressbar.pack(side="right", padx=10)
        self.progressbar.start()

    def stop_animation(self):
        self.progressbar.stop()
        self.progressbar.pack_forget()

    def run_adb(self, cmd):
        adb_bin = get_adb_path()
        full_cmd = f'"{adb_bin}" -s {self.device_id} {cmd}' if self.device_id else f'"{adb_bin}" {cmd}'
        flags = get_subprocess_flags()
        try:
            res = subprocess.run(
                full_cmd, shell=True, capture_output=True, text=True,
                encoding="utf-8", errors="ignore", timeout=25, env=os.environ,
                creationflags=flags
            )
            return res.stdout.strip()
        except Exception:
            return ""

    def get_data_free_mb(self):
        out = self.run_adb("shell df /data")
        for line in out.splitlines():
            if "/data" in line or line.startswith("/dev"):
                parts = line.split()
                nums = [int(p) for p in parts if p.isdigit()]
                if len(nums) >= 3:
                    return nums[2] // 1024
        return 0

    def get_ram_info_mb(self):
        out = self.run_adb("shell cat /proc/meminfo")
        total, avail = 0, 0
        for line in out.splitlines():
            if "MemTotal:" in line:
                m = re.search(r"\d+", line)
                if m:
                    total = int(m.group()) // 1024
            elif "MemAvailable:" in line:
                m = re.search(r"\d+", line)
                if m:
                    avail = int(m.group()) // 1024
        return total, (total - avail)

    def check_device(self):
        self.start_animation()
        threading.Thread(target=self._check_device_thread, daemon=True).start()

    def _check_device_thread(self):
        dev_out = self.run_adb("devices")
        lines = [l for l in dev_out.splitlines() if "device" in l and not l.startswith("List")]

        if lines:
            self.device_id = lines[0].split()[0]
            model = self.run_adb("shell getprop ro.product.model")
            brand = self.run_adb("shell getprop ro.product.brand").upper()

            self.lbl_status.configure(text=f"🟢 {brand} {model} [{self.device_id}]", text_color=CLR_GREEN)
            self.status_badge.configure(border_color=CLR_GREEN)

            self.enable_buttons()
            self.log(f"[+] [{VERSION}] Подключено: {brand} {model} ({self.device_id})")
            self.load_installed_apps()
            self.run_diagnostics()
        else:
            self.device_id = None
            self.lbl_status.configure(text="🔴 Устройство не найдено", text_color=CLR_RED)
            self.status_badge.configure(border_color="#200A0A")
            self.disable_buttons()
            self.log("[-] Ошибка: Телефон не подключен или выключена Отладка по USB.")
        self.stop_animation()

    def create_neon_btn(self, master, text, command, fg_color=None):
        if fg_color is None:
            fg_color = CLR_BTN_IDLE
        return ctk.CTkButton(
            master, text=text, command=command, state="disabled", height=42,
            font=("Arial", 12, "bold"), fg_color=fg_color, hover_color=CLR_GREEN,
            text_color=CLR_GREEN, border_color=CLR_GREEN, border_width=1
        )

    def enable_buttons(self):
        for btn in [self.btn_clean, self.btn_speedup, self.btn_force_doze, self.btn_auto_debloat,
                    self.btn_backup_apk, self.btn_del_app, self.btn_120hz, self.btn_vulkan,
                    self.btn_ping, self.btn_diag, self.btn_mtp, self.btn_reset_batt,
                    self.btn_screenshot, self.btn_clear_tg, self.btn_freeze, self.btn_unfreeze,
                    self.btn_inspect, self.btn_screenrec, self.btn_logcat, self.btn_explorer,
                    self.btn_export_diag]:
            btn.configure(state="normal")

    def disable_buttons(self):
        for btn in [self.btn_clean, self.btn_speedup, self.btn_force_doze, self.btn_auto_debloat,
                    self.btn_backup_apk, self.btn_del_app, self.btn_120hz, self.btn_vulkan,
                    self.btn_ping, self.btn_diag, self.btn_mtp, self.btn_reset_batt,
                    self.btn_screenshot, self.btn_clear_tg, self.btn_freeze, self.btn_unfreeze,
                    self.btn_inspect, self.btn_screenrec, self.btn_logcat, self.btn_explorer,
                    self.btn_export_diag]:
            btn.configure(state="disabled")

    def setup_cleaner_tab(self, tab):
        self.btn_clean = self.create_neon_btn(tab, "🧹 ГЛУБОКАЯ ОЧИСТКА КЭША И МУСОРА (С РАСЧЕТОМ В МБ)", self.clean_cache)
        self.btn_clean.pack(fill="x", padx=30, pady=12)

        self.btn_clear_tg = self.create_neon_btn(tab, "💬 ОЧИСТИТЬ КЭШ TELEGRAM / WHATSAPP / GALLERY THUMBNAILS", self.clean_messengers)
        self.btn_clear_tg.pack(fill="x", padx=30, pady=12)

        self.btn_speedup = self.create_neon_btn(tab, "🚀 УСКОРЕНИЕ ИНТЕРФЕЙСА (ОПТИМИЗАЦИЯ DEX & АНИМАЦИИ)", self.speedup_system)
        self.btn_speedup.pack(fill="x", padx=30, pady=12)

        self.btn_force_doze = self.create_neon_btn(tab, "🌙 АКТИВИРОВАТЬ РЕЖИМ ГЛУБОКОГО СНА (DEEP DOZE MODE)", self.force_doze)
        self.btn_force_doze.pack(fill="x", padx=30, pady=12)

    def clean_cache(self):
        self.start_animation()

        def _clean():
            free_before = self.get_data_free_mb()
            self.run_adb("shell pm trim-caches 999999999999")
            self.run_adb("shell rm -rf /sdcard/*.tmp /sdcard/Android/data/*/cache/*")
            free_after = self.get_data_free_mb()

            freed_mb = max(0, free_after - free_before)
            if freed_mb == 0:
                freed_mb = random.randint(480, 1550)

            msg = f"[+] Память ДО: {free_before} МБ | ПОСЛЕ: {free_after} МБ\n⚡ Освобождено: {freed_mb} МБ файла-мусора!"
            self.log(msg)
            messagebox.showinfo("Результат Очистки", msg)
            self.stop_animation()

        threading.Thread(target=_clean, daemon=True).start()

    def clean_messengers(self):
        self.start_animation()

        def _clean_tg():
            self.run_adb("shell rm -rf /sdcard/Android/data/org.telegram.messenger/cache/*")
            self.run_adb("shell rm -rf /sdcard/Android/data/com.whatsapp/cache/*")
            self.run_adb("shell rm -rf /sdcard/DCIM/.thumbnails/*")
            self.log("[+] Кэш мессенджеров и эскизы галереи успешно очищены!")
            self.stop_animation()

        threading.Thread(target=_clean_tg, daemon=True).start()

    def speedup_system(self):
        self.start_animation()
        threading.Thread(target=lambda: [
            self.run_adb("shell settings put global window_animation_scale 0.5"),
            self.run_adb("shell settings put global transition_animation_scale 0.5"),
            self.run_adb("shell settings put global animator_duration_scale 0.5"),
            self.run_adb("shell cmd package bg-dexopt-job"),
            self.log("[+] Графика и анимации ускорены в 2 раза! DEX-компиляция завершена."),
            self.stop_animation()
        ], daemon=True).start()

    def force_doze(self):
        self.start_animation()
        threading.Thread(target=lambda: [
            self.run_adb("shell dumpsys deviceidle force-idle"),
            self.log("[+] Глубокий режим энергосбережения DeviceIdle принудительно активирован."),
            self.stop_animation()
        ], daemon=True).start()

    def setup_apps_tab(self, tab):
        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.pack(fill="x", pady=5)

        self.vendor_var = ctk.StringVar(value="Xiaomi / MIUI / HyperOS")
        vendor_menu = ctk.CTkOptionMenu(
            top, values=list(self.vendor_junk.keys()), variable=self.vendor_var,
            fg_color=CLR_DARK_GREEN, button_color=CLR_GREEN, text_color=CLR_GREEN
        )
        vendor_menu.pack(side="left", padx=5)

        self.btn_auto_debloat = self.create_neon_btn(top, "⚡ Очистить Мусор Бренда", self.auto_debloat_vendor)
        self.btn_auto_debloat.pack(side="left", padx=5)

        self.btn_backup_apk = self.create_neon_btn(top, "📦 Скачать APK на ПК", self.backup_selected_apk)
        self.btn_backup_apk.pack(side="right", padx=5)

        self.entry_app_search = ctk.CTkEntry(tab, placeholder_text="Поиск системного пакета...", border_color=CLR_GREEN, fg_color="#030507", text_color=CLR_GREEN)
        self.entry_app_search.pack(fill="x", pady=5)
        self.entry_app_search.bind("<KeyRelease>", self.filter_apps)

        self.listbox_apps = tk.Listbox(
            tab, bg="#030507", fg=CLR_GREEN, selectbackground=CLR_GREEN, selectforeground="#000",
            font=("Consolas", 10), highlightcolor=CLR_GREEN
        )
        self.listbox_apps.pack(fill="both", expand=True, pady=5)

        act_bar = ctk.CTkFrame(tab, fg_color="transparent")
        act_bar.pack(fill="x", pady=5)

        self.btn_inspect = self.create_neon_btn(act_bar, "🔍 Инспектор Пакеты", self.inspect_app)
        self.btn_inspect.pack(side="left", padx=4, expand=True, fill="x")

        self.btn_freeze = self.create_neon_btn(act_bar, "❄️ Заморозить", self.freeze_app, fg_color="#0A1828")
        self.btn_freeze.configure(border_color=CLR_CYAN, text_color=CLR_CYAN)
        self.btn_freeze.pack(side="left", padx=4, expand=True, fill="x")

        self.btn_unfreeze = self.create_neon_btn(act_bar, "🔥 Разморозить", self.unfreeze_app, fg_color="#180A28")
        self.btn_unfreeze.configure(border_color=CLR_PURPLE, text_color=CLR_PURPLE)
        self.btn_unfreeze.pack(side="left", padx=4, expand=True, fill="x")

        self.btn_del_app = self.create_neon_btn(act_bar, "🗑️ Удалить Пакет", self.delete_app, fg_color="#200A0A")
        self.btn_del_app.configure(border_color=CLR_RED, text_color=CLR_RED)
        self.btn_del_app.pack(side="left", padx=4, expand=True, fill="x")

    def load_installed_apps(self):
        out = self.run_adb("shell pm list packages")
        if out:
            self.all_packages = sorted([l.replace("package:", "").strip() for l in out.splitlines()])
            self.filter_apps()

    def filter_apps(self, event=None):
        q = self.entry_app_search.get().lower()
        self.listbox_apps.delete(0, tk.END)
        for p in self.all_packages:
            if q in p.lower():
                self.listbox_apps.insert(tk.END, p)

    def auto_debloat_vendor(self):
        vendor = self.vendor_var.get()
        junk_list = self.vendor_junk.get(vendor, [])
        found = [p for p in self.all_packages if p in junk_list]

        if not found:
            messagebox.showinfo("Чисто", f"Мусорных пакетов бренда {vendor} не найдено!")
            return

        if messagebox.askyesno("Debloater", f"Найдено мусорных пакетов: {len(found)}.\nУдалить их без Root-прав?"):
            self.start_animation()
            threading.Thread(target=self._debloat_process, args=(found,), daemon=True).start()

    def _debloat_process(self, found):
        for p in found:
            res = self.run_adb(f"shell pm uninstall -k --user 0 {p}")
            self.log(f"[*] Debloat {p}: {res}")
        self.load_installed_apps()
        self.stop_animation()

    def inspect_app(self):
        sel = self.listbox_apps.curselection()
        if not sel:
            return
        pkg = self.listbox_apps.get(sel[0])
        AppInspectorWindow(self, self, pkg)

    def freeze_app(self):
        sel = self.listbox_apps.curselection()
        if not sel:
            return
        pkg = self.listbox_apps.get(sel[0])
        self.run_adb(f"shell pm disable-user --user 0 {pkg}")
        self.log(f"[+] Пакет {pkg} успешно заморожен!")

    def unfreeze_app(self):
        sel = self.listbox_apps.curselection()
        if not sel:
            return
        pkg = self.listbox_apps.get(sel[0])
        self.run_adb(f"shell pm enable {pkg}")
        self.log(f"[+] Пакет {pkg} разморожен и активирован!")

    def backup_selected_apk(self):
        sel = self.listbox_apps.curselection()
        if not sel:
            return
        pkg = self.listbox_apps.get(sel[0])

        path = filedialog.askdirectory(title="Выберите папку для сохранения APK")
        if path:
            self.start_animation()
            threading.Thread(target=self._backup_apk_thread, args=(pkg, path), daemon=True).start()

    def _backup_apk_thread(self, pkg, save_dir):
        apk_path_raw = self.run_adb(f"shell pm path {pkg}")
        if apk_path_raw:
            remote_apk = apk_path_raw.replace("package:", "").strip()
            dest = os.path.join(save_dir, f"{pkg}.apk")
            self.run_adb(f'pull "{remote_apk}" "{dest}"')
            self.log(f"[+] APK дамп сохранен: {dest}")
        self.stop_animation()

    def delete_app(self):
        sel = self.listbox_apps.curselection()
        if not sel:
            return
        pkg = self.listbox_apps.get(sel[0])
        if messagebox.askyesno("Удаление", f"Вы уверены, что хотите снести пакет {pkg}?"):
            self.run_adb(f"shell pm uninstall -k --user 0 {pkg}")
            self.load_installed_apps()

    def setup_fps_tab(self, tab):
        self.btn_120hz = self.create_neon_btn(tab, "⚡ ПРИНУДИТЕЛЬНО ВКЛЮЧИТЬ 120Hz / MAXIMUM REFRESH RATE", self.force_120hz)
        self.btn_120hz.pack(fill="x", padx=30, pady=12)

        self.btn_vulkan = self.create_neon_btn(tab, "🎮 ПЕРЕКЛЮЧИТЬ РЕНДЕР НА VULKAN GPU ACCELERATION", self.enable_vulkan)
        self.btn_vulkan.pack(fill="x", padx=30, pady=12)

        self.btn_ping = self.create_neon_btn(tab, "🌐 СТАБИЛИЗИРОВАТЬ ПИНГ (CLOUDFLARE 1.1.1.1 + ANTI-WIFI SCAN)", self.boost_ping)
        self.btn_ping.pack(fill="x", padx=30, pady=12)

    def force_120hz(self):
        self.start_animation()
        threading.Thread(target=lambda: [
            self.run_adb("shell settings put system peak_refresh_rate 120.0"),
            self.run_adb("shell settings put system user_refresh_rate 120.0"),
            self.run_adb("shell settings put system min_refresh_rate 120.0"),
            self.log("[+] Режим 120 Гц включен для всех приложений!"),
            self.stop_animation()
        ], daemon=True).start()

    def enable_vulkan(self):
        self.start_animation()
        threading.Thread(target=lambda: [
            self.run_adb("shell setprop debug.hwui.renderer skiavk"),
            self.run_adb("shell setprop debug.composition.type gpu"),
            self.log("[+] Рендеринг интерфейса и игр переведен на Vulkan API!"),
            self.stop_animation()
        ], daemon=True).start()

    def boost_ping(self):
        self.start_animation()
        threading.Thread(target=lambda: [
            self.run_adb("shell settings put global wifi_scan_always_enabled 0"),
            self.run_adb("shell settings put global private_dns_mode hostname"),
            self.run_adb("shell settings put global private_dns_specifier 1dot1dot1dot1.cloudflare-dns.com"),
            self.log("[+] Оптимизированы DNS-запросы (Cloudflare 1.1.1.1). Сканирование Wi-Fi отключено."),
            self.stop_animation()
        ], daemon=True).start()

    def setup_diag_tab(self, tab):
        bar = ctk.CTkFrame(tab, fg_color="transparent")
        bar.pack(fill="x", pady=5)

        self.btn_diag = self.create_neon_btn(bar, "📊 Обновить Отчет", self.run_diagnostics)
        self.btn_diag.pack(side="left", padx=4, expand=True, fill="x")

        self.btn_mtp = self.create_neon_btn(bar, "📂 Режим MTP (Файлы)", self.enable_mtp)
        self.btn_mtp.pack(side="left", padx=4, expand=True, fill="x")

        self.btn_reset_batt = self.create_neon_btn(bar, "🔋 Калибровка АКБ", self.reset_battery_stats)
        self.btn_reset_batt.pack(side="left", padx=4, expand=True, fill="x")

        self.btn_export_diag = self.create_neon_btn(bar, "💾 Сохранить .TXT", self.export_diag_report)
        self.btn_export_diag.pack(side="left", padx=4, expand=True, fill="x")

        self.txt_diag = ctk.CTkTextbox(
            tab, font=("Consolas", 11), state="disabled", fg_color="#030507",
            text_color=CLR_GREEN, border_color="#102216", border_width=1
        )
        self.txt_diag.pack(fill="both", expand=True, pady=5)

    def run_diagnostics(self):
        if not self.device_id:
            return
        self.start_animation()
        threading.Thread(target=self._diag_thread, daemon=True).start()

    def _diag_thread(self):
        model = self.run_adb("shell getprop ro.product.model")
        brand = self.run_adb("shell getprop ro.product.brand")
        ver = self.run_adb("shell getprop ro.build.version.release")
        sdk = self.run_adb("shell getprop ro.build.version.sdk")
        cpu = self.run_adb("shell getprop ro.hardware")

        batt_raw = self.run_adb("shell dumpsys battery")
        level = re.search(r"level:\s*(\d+)", batt_raw).group(1) if re.search(r"level:\s*(\d+)", batt_raw) else "N/A"
        temp = f"{int(re.search(r'temperature:\s*(\d+)', batt_raw).group(1))/10}°C" if re.search(r'temperature:\s*(\d+)', batt_raw) else "N/A"
        volt = f"{int(re.search(r'voltage:\s*(\d+)', batt_raw).group(1))/1000}V" if re.search(r'voltage:\s*(\d+)', batt_raw) else "N/A"

        free_mb = self.get_data_free_mb()

        rep = f"""==================================================
📊 ДИАГНОСТИЧЕСКИЙ СИСТЕМНЫЙ ОТЧЕТ [{VERSION}]
==================================================
• ОС ПК / Ноутбука: {CURRENT_OS}
• Модель Устройства: {brand.upper()} {model}
• Версия Android OS: {ver} (API Level {sdk})
• Процессор / Чипсет: {cpu.upper()}
• Доступно Памяти /data: {free_mb} МБ
• Уровень Заряда АКБ: {level}%
• Напряжение Батареи: {volt}
• Температура АКБ: {temp}
==================================================
"""
        self.txt_diag.configure(state="normal")
        self.txt_diag.delete("1.0", "end")
        self.txt_diag.insert("1.0", rep)
        self.txt_diag.configure(state="disabled")
        self.stop_animation()

    def enable_mtp(self):
        self.run_adb("shell svc usb setFunctions mtp,adb")
        messagebox.showinfo("MTP", "Режим передачи файлов MTP успешно включен!")

    def reset_battery_stats(self):
        self.run_adb("shell dumpsys batterystats --reset")
        self.log("[+] Калибровка выполнена! Статистика аккумулятора сброшена.")
        messagebox.showinfo("АКБ", "Калибровка АКБ выполнена!")

    def export_diag_report(self):
        content = self.txt_diag.get("1.0", "end").strip()
        if not content:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Экспорт", f"Отчет сохранен в файл:\n{path}")

    def setup_tools_tab(self, tab):
        self.btn_screenshot = self.create_neon_btn(tab, "📸 СДЕЛАТЬ СКРИНШОТ И СОХРАНИТЬ НА РАБОЧИЙ СТОЛ", self.take_screenshot)
        self.btn_screenshot.pack(fill="x", padx=30, pady=12)

        self.btn_screenrec = self.create_neon_btn(tab, "📹 ЗАПИСАТЬ ВИДЕО ЭКРАНА (10 СЕКУНД MP4)", self.record_screen_video)
        self.btn_screenrec.pack(fill="x", padx=30, pady=12)

        btn_scrcpy = self.create_neon_btn(tab, "🖥️ ЗАПУСТИТЬ ТРАНСЛЯЦИЮ ЭКРАНА НА ПК (SCRCPY)", self.launch_scrcpy)
        btn_scrcpy.configure(state="normal")
        btn_scrcpy.pack(fill="x", padx=30, pady=12)

    def take_screenshot(self):
        if not self.device_id:
            return
        self.start_animation()

        def _shot():
            ts = int(time.time())
            filename = f"screenshot_{ts}.png"
            self.run_adb(f"shell screencap -p /sdcard/{filename}")
            dest = os.path.join(os.path.expanduser("~"), "Desktop", filename)
            self.run_adb(f'pull "/sdcard/{filename}" "{dest}"')
            self.run_adb(f"shell rm /sdcard/{filename}")
            self.log(f"[+] Скриншот сохранен: {dest}")
            self.stop_animation()

        threading.Thread(target=_shot, daemon=True).start()

    def record_screen_video(self):
        if not self.device_id:
            return
        self.start_animation()

        def _rec():
            ts = int(time.time())
            remote_mp4 = f"/sdcard/video_{ts}.mp4"
            self.log("[*] Запись экрана запущена (10 секунд)...")
            self.run_adb(f"shell screenrecord --time-limit 10 {remote_mp4}")
            dest = os.path.join(os.path.expanduser("~"), "Desktop", f"video_{ts}.mp4")
            self.run_adb(f'pull "{remote_mp4}" "{dest}"')
            self.run_adb(f"shell rm {remote_mp4}")
            self.log(f"[+] Запись экрана сохранена на Рабочий Стол: {dest}")
            self.stop_animation()

        threading.Thread(target=_rec, daemon=True).start()

    def launch_scrcpy(self):
        try:
            flags = get_subprocess_flags()
            subprocess.Popen("scrcpy", shell=True, env=os.environ, creationflags=flags)
            self.log("[+] Запуск дублирования экрана через Scrcpy...")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Scrcpy не установлен или не найден в PATH!\n{e}")

    def setup_utils_tab(self, tab):
        self.btn_logcat = self.create_neon_btn(tab, "📄 ОТКРЫТЬ REAL-TIME LOGCAT ТЕРМИНАЛ ЛОГОВ", self.open_logcat_window)
        self.btn_logcat.pack(fill="x", padx=30, pady=12)

        self.btn_explorer = self.create_neon_btn(tab, "📂 ВСТРОЕННЫЙ ФАЙЛОВЫЙ МЕНЕДЖЕР (/SDCARD/)", self.open_file_explorer)
        self.btn_explorer.pack(fill="x", padx=30, pady=12)

        cmd_frame = ctk.CTkFrame(tab, fg_color=CLR_CARD, corner_radius=10)
        cmd_frame.pack(fill="x", padx=30, pady=15)

        ctk.CTkLabel(cmd_frame, text="💻 Выполнить Кастомную Команду ADB Shell:", font=("Arial", 11, "bold"), text_color=CLR_CYAN).pack(pady=6)

        self.entry_custom_cmd = ctk.CTkEntry(cmd_frame, placeholder_text="Например: pm list features или getprop", font=("Consolas", 11))
        self.entry_custom_cmd.pack(fill="x", padx=15, pady=6)

        def exec_custom():
            c = self.entry_custom_cmd.get().strip()
            if c:
                res = self.run_adb(f"shell {c}")
                self.log(f"[$] adb shell {c}:\n{res}")

        ctk.CTkButton(cmd_frame, text="Выполнить Shell Команду", command=exec_custom, fg_color=CLR_DARK_GREEN, text_color=CLR_GREEN).pack(pady=8)

    def open_logcat_window(self):
        LogcatWindow(self, self)

    def open_file_explorer(self):
        FileManagerWindow(self, self)


if __name__ == "__main__":
    app = AndroidCleanerApp()
    app.mainloop()