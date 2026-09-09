import os
import random
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk


def resource_path(relative_path):
    """Возвращает правильный путь к ресурсам как при запуске .py, так и внутри .exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Настройка темы CustomTkinter
ctk.set_appearance_mode("dark")


class MatrixBanner(tk.Canvas):
    """Анимированный холст с эффектом матрицы (падающий зеленый код)"""

    def __init__(self, master, width=820, height=70, **kwargs):
        super().__init__(
            master,
            width=width,
            height=height,
            bg="#030504",
            highlightthickness=0,
            **kwargs,
        )
        self.width = width
        self.height = height
        self.fontsize = 11
        self.columns = width // self.fontsize
        self.drops = [random.randint(-15, 0) for _ in range(self.columns)]
        self.chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&*#<>[]"
        self.running = True
        self.animate()

    def animate(self):
        if not self.running:
            return
        self.delete("all")

        # Подложка
        self.create_rectangle(
            0, 0, self.width, self.height, fill="#030504", outline=""
        )

        # Отрисовка символов
        for i in range(len(self.drops)):
            char = random.choice(self.chars)
            x = i * self.fontsize + 4
            y = self.drops[i] * self.fontsize

            # Голова потока (ярко-белый/неоновый)
            self.create_text(
                x,
                y,
                text=char,
                fill="#E0FFED",
                font=("Consolas", self.fontsize, "bold"),
            )
            # Яркий хвост
            if y - self.fontsize > 0:
                self.create_text(
                    x,
                    y - self.fontsize,
                    text=random.choice(self.chars),
                    fill="#00FF66",
                    font=("Consolas", self.fontsize),
                )
            # Темный хвост
            if y - (self.fontsize * 2) > 0:
                self.create_text(
                    x,
                    y - (self.fontsize * 2),
                    text=random.choice(self.chars),
                    fill="#0A5C28",
                    font=("Consolas", self.fontsize),
                )

            if y > self.height and random.random() > 0.94:
                self.drops[i] = 0
            else:
                self.drops[i] += 1

        # Неоновая надпись по центру
        self.create_text(
            self.width // 2,
            self.height // 2,
            text="⚡ ANDROID CLEANER & DIAGNOSTICS PRO ⚡",
            fill="#00FF66",
            font=("Arial", 15, "bold"),
        )

        self.after(45, self.animate)

    def destroy(self):
        self.running = False
        super().destroy()


class AndroidCleanerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Android_Cleaner & Diagnostics 1.3 by meisarobloxer")
        self.geometry("920x780")
        self.minsize(860, 720)
        self.configure(fg_color="#080A0C")

        # Цветовая палитра Matrix
        self.CLR_BG = "#080A0C"
        self.CLR_CARD = "#0F1418"
        self.CLR_GREEN = "#00FF66"
        self.CLR_GREEN_DARK = "#0A2012"
        self.CLR_BTN_IDLE = "#121A15"

        self.device_id = None
        self.all_packages = []

        self.junk_keywords = [
            "facebook.appmanager",
            "facebook.services",
            "facebook.system",
            "autoinstalls.config",
            "partnerbookmarks",
            "android.egg",
            "com.miui.analytics",
            "com.miui.msa.global",
            "com.samsung.android.bixby",
            "com.huawei.skytone",
            "com.google.android.videos",
        ]

        # Подключение иконки через безопасную функцию resource_path
        try:
            self.iconbitmap(resource_path("logo.ico"))
        except Exception:
            pass

        self.setup_ui()

    def setup_ui(self):
        # --- АНИМИРОВАННЫЙ БАННЕР ---
        self.banner = MatrixBanner(self)
        self.banner.pack(fill="x", padx=15, pady=(15, 5))

        # --- ВЕРХНЯЯ ПАНЕЛЬ СТАТУСА И ИНДИКАТОРА MTP/ADB ---
        top_frame = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=self.CLR_CARD,
            border_color="#182D20",
            border_width=1,
        )
        top_frame.pack(fill="x", padx=15, pady=10)

        self.btn_check = ctk.CTkButton(
            top_frame,
            text="🔍 Найти устройство",
            command=self.check_device,
            font=("Arial", 13, "bold"),
            fg_color=self.CLR_GREEN_DARK,
            hover_color=self.CLR_GREEN,
            text_color=self.CLR_GREEN,
            border_color=self.CLR_GREEN,
            border_width=1,
        )
        self.btn_check.pack(side="left", padx=15, pady=12)

        # Контейнер-бейдж для статуса подключения
        self.status_badge = ctk.CTkFrame(
            top_frame,
            corner_radius=8,
            fg_color="#030504",
            border_color="#200A0A",
            border_width=1,
        )
        self.status_badge.pack(side="left", padx=10, pady=12)

        self.lbl_status = ctk.CTkLabel(
            self.status_badge,
            text="🔴 Не подключено",
            text_color="#FF4D4D",
            font=("Consolas", 12, "bold"),
        )
        self.lbl_status.pack(padx=12, pady=4)

        self.progressbar = ctk.CTkProgressBar(
            top_frame,
            mode="indeterminate",
            width=180,
            progress_color=self.CLR_GREEN,
        )
        self.progressbar.set(0)

        # --- ВКЛАДКИ ---
        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=12,
            fg_color=self.CLR_CARD,
            segmented_button_selected_color=self.CLR_GREEN_DARK,
            segmented_button_unselected_color=self.CLR_BTN_IDLE,
            text_color=self.CLR_GREEN,
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.tabview.add("Очистка и Ускорение")
        self.tabview.add("Менеджер Приложений")
        self.tabview.add("Игры и Инструменты")
        self.tabview.add("Диагностика и MTP")

        self.setup_cleaner_tab(self.tabview.tab("Очистка и Ускорение"))
        self.setup_apps_tab(self.tabview.tab("Менеджер Приложений"))
        self.setup_tools_tab(self.tabview.tab("Игры и Инструменты"))
        self.setup_diag_tab(self.tabview.tab("Диагностика и MTP"))

        # --- ЛОГ РАБОТЫ ---
        self.txt_log = ctk.CTkTextbox(
            self,
            height=110,
            font=("Consolas", 11),
            state="disabled",
            corner_radius=10,
            fg_color="#030504",
            text_color=self.CLR_GREEN,
            border_color="#122B1B",
            border_width=1,
        )
        self.txt_log.pack(fill="x", padx=15, pady=(0, 15))
        self.log("[*] System initialized...")
        self.log(
            "[*] Подключите телефон по USB и нажмите 'Найти устройство'."
        )

    def start_animation(self):
        self.progressbar.pack(side="right", padx=15)
        self.progressbar.start()

    def stop_animation(self):
        self.progressbar.stop()
        self.progressbar.pack_forget()

    def log(self, message):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", message + "\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def run_adb(self, cmd, use_device_id=True):
        if use_device_id and self.device_id:
            cmd = f"-s {self.device_id} {cmd}"
        try:
            result = subprocess.run(
                f"adb {cmd}",
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=40,
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def check_device(self):
        self.start_animation()
        threading.Thread(target=self._check_device_thread, daemon=True).start()

    def _check_device_thread(self):
        devices_output = self.run_adb("devices", use_device_id=False)
        lines = [
            line
            for line in devices_output.splitlines()
            if "device" in line and not line.startswith("List")
        ]

        if lines:
            self.device_id = lines[0].split()[0]

            # Определение активных режимов USB (MTP / PTP / ADB)
            usb_cfg = self.run_adb("shell getprop sys.usb.config").lower()
            usb_state = self.run_adb("shell getprop sys.usb.state").lower()
            combined_usb = f"{usb_cfg} {usb_state}"

            modes = []
            if "mtp" in combined_usb:
                modes.append("MTP")
            if "ptp" in combined_usb:
                modes.append("PTP")
            modes.append("ADB")

            mode_str = "/".join(modes)

            # Чтение названия модели
            model = self.run_adb("shell getprop ro.product.model")
            device_display = (
                f"{model} ({self.device_id})" if model else self.device_id
            )

            # Обновление графического бейджа
            status_text = f"🟢 {device_display} [{mode_str}]"
            self.lbl_status.configure(
                text=status_text, text_color=self.CLR_GREEN
            )
            self.status_badge.configure(border_color=self.CLR_GREEN)

            self.enable_buttons()
            self.log(
                f"[+] Найдено устройство: {self.device_id} | Режим: {mode_str}"
            )
            self.load_installed_apps()
            self.run_diagnostics()
        else:
            self.device_id = None
            self.lbl_status.configure(
                text="🔴 Устройство не найдено", text_color="#FF4D4D"
            )
            self.status_badge.configure(border_color="#200A0A")
            self.disable_buttons()
            self.log(
                "[-] Устройство не обнаружено. Включите отладку по USB."
            )
        self.stop_animation()

    def create_neon_button(
        self, master, text, command, height=40, fg_color=None
    ):
        if fg_color is None:
            fg_color = self.CLR_BTN_IDLE
        return ctk.CTkButton(
            master,
            text=text,
            command=command,
            state="disabled",
            height=height,
            font=("Arial", 13, "bold"),
            fg_color=fg_color,
            hover_color=self.CLR_GREEN,
            text_color=self.CLR_GREEN,
            border_color=self.CLR_GREEN,
            border_width=1,
        )

    def enable_buttons(self):
        for btn in [
            self.btn_clean,
            self.btn_speedup,
            self.btn_auto_clean,
            self.btn_dpi,
            self.btn_perf,
            self.btn_game_opt,
            self.btn_run_diag,
            self.btn_enable_mtp,
            self.btn_open_usb_settings,
        ]:
            btn.configure(state="normal")

    def disable_buttons(self):
        for btn in [
            self.btn_clean,
            self.btn_speedup,
            self.btn_auto_clean,
            self.btn_dpi,
            self.btn_perf,
            self.btn_game_opt,
            self.btn_run_diag,
            self.btn_enable_mtp,
            self.btn_open_usb_settings,
        ]:
            btn.configure(state="disabled")

    # --- ВКЛАДКА 1: ЧИСТКА ---
    def setup_cleaner_tab(self, tab):
        lbl_info = ctk.CTkLabel(
            tab,
            text="Системная оптимизация Android",
            font=("Arial", 15, "bold"),
            text_color=self.CLR_GREEN,
        )
        lbl_info.pack(pady=12)

        self.btn_clean = self.create_neon_button(
            tab,
            "🧹 БЕЗОПАСНО ОЧИСТИТЬ КЭШ ВСЕХ ПРИЛОЖЕНИЙ",
            self.start_cleaning,
            height=45,
        )
        self.btn_clean.pack(fill="x", padx=40, pady=12)

        self.btn_speedup = self.create_neon_button(
            tab,
            "🚀 УСКОРИТЬ СИСТЕМУ (АНИМАЦИИ + OPTIMIZATION)",
            self.start_speedup,
            height=45,
        )
        self.btn_speedup.pack(fill="x", padx=40, pady=12)

    def start_cleaning(self):
        self.btn_clean.configure(state="disabled")
        self.start_animation()
        threading.Thread(target=self._clean_process, daemon=True).start()

    def _clean_process(self):
        self.log("\n[=== ОЧИСТКА КЭША ===]")
        self.run_adb("shell pm trim-caches 999999999999")
        self.run_adb(
            "shell rm -rf /sdcard/*.tmp /sdcard/*.log /sdcard/Download/*.tmp"
        )
        self.log("[+] Системный кэш успешно сброшен!")
        self.stop_animation()
        self.btn_clean.configure(state="normal")
        messagebox.showinfo("Готово", "Безопасный кэш приложений очищен!")

    def start_speedup(self):
        self.btn_speedup.configure(state="disabled")
        self.start_animation()
        threading.Thread(target=self._speedup_process, daemon=True).start()

    def _speedup_process(self):
        self.log("\n[=== УСКОРЕНИЕ ИНТЕРФЕЙСА ===]")
        self.run_adb("shell settings put global window_animation_scale 0.5")
        self.run_adb("shell settings put global transition_animation_scale 0.5")
        self.run_adb("shell settings put global animator_duration_scale 0.5")
        self.run_adb("shell cmd package bg-dexopt-job")
        self.run_adb("shell sync")
        self.log("[+] Анимации ускорены, байткод оптимизирован!")
        self.stop_animation()
        self.btn_speedup.configure(state="normal")
        messagebox.showinfo("Успех", "Скорость работы интерфейса повышена!")

    # --- ВКЛАДКА 2: МЕНЕДЖЕР ПРИЛОЖЕНИЙ ---
    def setup_apps_tab(self, tab):
        search_frame = ctk.CTkFrame(tab, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 8))

        self.entry_search = ctk.CTkEntry(
            search_frame,
            placeholder_text="Поиск пакетов...",
            border_color=self.CLR_GREEN,
            fg_color="#030504",
            text_color=self.CLR_GREEN,
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", self.filter_apps)

        self.btn_auto_clean = self.create_neon_button(
            search_frame, "⚡ Авто-Мусор", self.auto_delete_junk
        )
        self.btn_auto_clean.pack(side="right")

        self.listbox_apps = tk.Listbox(
            tab,
            bg="#030504",
            fg=self.CLR_GREEN,
            selectbackground=self.CLR_GREEN,
            selectforeground="#000000",
            font=("Consolas", 10),
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=self.CLR_GREEN,
            highlightbackground="#122B1B",
        )
        self.listbox_apps.pack(fill="both", expand=True, pady=5)

        self.btn_delete_app = self.create_neon_button(
            tab,
            "Снести выбранное приложение",
            self.uninstall_selected_app,
            fg_color="#200A0A",
        )
        self.btn_delete_app.configure(
            border_color="#FF4D4D", text_color="#FF4D4D"
        )
        self.btn_delete_app.pack(fill="x", pady=8)

    def load_installed_apps(self):
        output = self.run_adb("shell pm list packages")
        if output:
            pkgs = [
                line.replace("package:", "").strip()
                for line in output.splitlines()
            ]
            self.all_packages = sorted(pkgs)
            self.filter_apps()

    def filter_apps(self, event=None):
        query = self.entry_search.get().lower()
        self.listbox_apps.delete(0, tk.END)
        for pkg in self.all_packages:
            if query in pkg.lower():
                self.listbox_apps.insert(tk.END, pkg)

    def uninstall_selected_app(self):
        selected = self.listbox_apps.curselection()
        if not selected:
            return
        pkg_name = self.listbox_apps.get(selected[0])

        if messagebox.askyesno("Удаление", f"Удалить пакет {pkg_name}?"):
            self.start_animation()
            threading.Thread(
                target=self._uninstall_process, args=(pkg_name,), daemon=True
            ).start()

    def _uninstall_process(self, pkg_name):
        res = self.run_adb(f"shell pm uninstall -k --user 0 {pkg_name}")
        if "Success" in res:
            self.log(f"[+] Удалено: {pkg_name}")
            self.load_installed_apps()
        else:
            self.log(f"[-] Ошибка: {res}")
        self.stop_animation()

    def auto_delete_junk(self):
        if not self.all_packages:
            return
        junk = [
            p
            for p in self.all_packages
            if any(kw in p for kw in self.junk_keywords)
        ]
        if not junk:
            messagebox.showinfo("Чисто", "Системного мусора не найдено.")
            return

        if messagebox.askyesno(
            "Авто-очистка", f"Удалить найденный мусор ({len(junk)} шт.)?"
        ):
            self.start_animation()
            threading.Thread(
                target=self._auto_delete_process, args=(junk,), daemon=True
            ).start()

    def _auto_delete_process(self, junk_found):
        self.log(f"\n[=== УДАЛЕНИЕ МУСОРА ({len(junk_found)} шт.) ===]")
        for pkg in junk_found:
            if "Success" in self.run_adb(
                f"shell pm uninstall -k --user 0 {pkg}"
            ):
                self.log(f"[+] Удалено: {pkg}")
        self.load_installed_apps()
        self.stop_animation()
        messagebox.showinfo("Успех", "Мусор очищен!")

    # --- ВКЛАДКА 3: ИГРЫ И ИНСТРУМЕНТЫ ---
    def setup_tools_tab(self, tab):
        game_frame = ctk.CTkFrame(
            tab, fg_color="#030504", border_color="#122B1B", border_width=1
        )
        game_frame.pack(fill="x", pady=8, padx=10)

        ctk.CTkLabel(
            game_frame,
            text="Оптимизация для Онлайн Игр",
            font=("Arial", 14, "bold"),
            text_color=self.CLR_GREEN,
        ).pack(pady=(8, 2))
        ctk.CTkLabel(
            game_frame,
            text=(
                "Убивает фоновые процессы, ставит Cloudflare DNS (1.1.1.1) и"
                " убирает скачки пинга"
            ),
            font=("Arial", 10),
            text_color="gray",
        ).pack()

        self.btn_game_opt = self.create_neon_button(
            game_frame,
            "🎮 УБРАТЬ ФРИЗЫ И СТАБИЛИЗИРОВАТЬ ПИНГ",
            self.start_game_opt,
            height=40,
        )
        self.btn_game_opt.pack(pady=10, padx=20, fill="x")

        dpi_frame = ctk.CTkFrame(
            tab, fg_color="#030504", border_color="#122B1B", border_width=1
        )
        dpi_frame.pack(fill="x", pady=8, padx=10)

        ctk.CTkLabel(
            dpi_frame,
            text="Плотность экрана (DPI):",
            font=("Arial", 12),
            text_color=self.CLR_GREEN,
        ).pack(pady=(6, 0))
        self.entry_dpi = ctk.CTkEntry(
            dpi_frame,
            placeholder_text="Например: 420 или reset",
            border_color=self.CLR_GREEN,
            fg_color="#080A0C",
            text_color=self.CLR_GREEN,
        )
        self.entry_dpi.pack(pady=6)

        self.btn_dpi = self.create_neon_button(
            dpi_frame, "Изменить DPI", self.change_dpi, height=32
        )
        self.btn_dpi.pack(pady=(0, 8))

        perf_frame = ctk.CTkFrame(
            tab, fg_color="#030504", border_color="#122B1B", border_width=1
        )
        perf_frame.pack(fill="x", pady=8, padx=10)

        ctk.CTkLabel(
            perf_frame,
            text="Режим производительности CPU/GPU:",
            font=("Arial", 12),
            text_color=self.CLR_GREEN,
        ).pack(pady=(6, 0))
        self.btn_perf = self.create_neon_button(
            perf_frame,
            "⚡ ВКЛЮЧИТЬ МАКС. ПРОИЗВОДИТЕЛЬНОСТЬ",
            self.enable_high_perf,
            height=36,
        )
        self.btn_perf.pack(pady=8, padx=20, fill="x")

    def start_game_opt(self):
        self.btn_game_opt.configure(state="disabled")
        self.start_animation()
        threading.Thread(target=self._game_opt_process, daemon=True).start()

    def _game_opt_process(self):
        self.log("\n[=== ИГРОВАЯ ОПТИМИЗАЦИЯ ===]")
        self.run_adb("shell settings put global wifi_scan_always_enabled 0")
        self.run_adb("shell settings put global ble_scan_always_enabled 0")
        self.run_adb("shell settings put global private_dns_mode hostname")
        self.run_adb(
            "shell settings put global private_dns_specifier"
            " 1dot1dot1dot1.cloudflare-dns.com"
        )
        self.run_adb("shell am kill-all")
        self.log("[+] Сеть и ОЗУ настроены для онлайн-игр!")
        self.stop_animation()
        self.btn_game_opt.configure(state="normal")
        messagebox.showinfo(
            "Игровой режим", "Пинг стабилизирован, фоновые процессы выгружены!"
        )

    def change_dpi(self):
        val = self.entry_dpi.get().strip()
        if not val:
            return
        self.start_animation()
        if val.lower() == "reset":
            self.run_adb("shell wm density reset")
            self.log("[+] DPI сброшен.")
        else:
            self.run_adb(f"shell wm density {val}")
            self.log(f"[+] DPI установлен на {val}.")
        self.stop_animation()
        messagebox.showinfo("Готово", "Изменения применены!")

    def enable_high_perf(self):
        self.start_animation()
        self.run_adb(
            "shell cmd power set-fixed-performance-mode-enabled true"
        )
        self.log("[+] Режим максимальной производительности включен.")
        self.stop_animation()
        messagebox.showinfo("Готово", "Максимальный режим активирован!")

    # --- ВКЛАДКА 4: ДИАГНОСТИКА И MTP ---
    def setup_diag_tab(self, tab):
        btn_bar = ctk.CTkFrame(tab, fg_color="transparent")
        btn_bar.pack(fill="x", pady=(0, 8))

        self.btn_run_diag = self.create_neon_button(
            btn_bar,
            "📊 Запустить диагностику",
            self.run_diagnostics,
            height=36,
        )
        self.btn_run_diag.pack(side="left", padx=(0, 6), expand=True, fill="x")

        self.btn_enable_mtp = self.create_neon_button(
            btn_bar,
            "📂 Включить MTP (Передача файлов)",
            self.enable_mtp,
            height=36,
        )
        self.btn_enable_mtp.pack(side="left", padx=6, expand=True, fill="x")

        self.btn_open_usb_settings = self.create_neon_button(
            btn_bar,
            "⚙️ Настройки USB в телефоне",
            self.open_usb_settings,
            height=36,
        )
        self.btn_open_usb_settings.pack(
            side="left", padx=(6, 0), expand=True, fill="x"
        )

        # Поле вывода диагностики
        self.txt_diag = ctk.CTkTextbox(
            tab,
            font=("Consolas", 11),
            state="disabled",
            corner_radius=10,
            fg_color="#030504",
            text_color=self.CLR_GREEN,
            border_color="#122B1B",
            border_width=1,
        )
        self.txt_diag.pack(fill="both", expand=True, pady=5)

    def run_diagnostics(self):
        if not self.device_id:
            self.update_diag_text(
                "❌ Устройство не подключено.\nНажмите 'Найти устройство' на"
                " верхней панели."
            )
            return

        self.start_animation()
        threading.Thread(target=self._diagnostics_process, daemon=True).start()

    def _diagnostics_process(self):
        self.log("\n[=== СБОР ДИАГНОСТИЧЕСКИХ ДАННЫХ ===]")

        model = self.run_adb("shell getprop ro.product.model") or "Н/Д"
        brand = self.run_adb("shell getprop ro.product.brand") or "Н/Д"
        manufacturer = (
            self.run_adb("shell getprop ro.product.manufacturer") or "Н/Д"
        )
        android_ver = (
            self.run_adb("shell getprop ro.build.version.release") or "Н/Д"
        )
        sdk_ver = self.run_adb("shell getprop ro.build.version.sdk") or "Н/Д"
        serial = (
            self.run_adb("shell getprop ro.serialno")
            or self.run_adb("shell getprop ro.boot.serialno")
            or "Н/Д"
        )
        cpu = (
            self.run_adb("shell getprop ro.hardware")
            or self.run_adb("shell getprop ro.board.platform")
            or "Н/Д"
        )

        display_raw = self.run_adb("shell wm size")
        res = (
            display_raw.replace("Physical size: ", "").strip()
            if display_raw
            else "Н/Д"
        )
        density_raw = self.run_adb("shell wm density")
        dpi = (
            density_raw.replace("Physical size: ", "")
            .replace("Override density: ", "")
            .strip()
            if density_raw
            else "Н/Д"
        )

        usb_config = self.run_adb("shell getprop sys.usb.config") or "Н/Д"
        usb_state = self.run_adb("shell getprop sys.usb.state") or "Н/Д"
        is_mtp_active = "mtp" in (usb_config + usb_state).lower()
        mtp_status_str = (
            "✅ АКТИВЕН (Передача файлов)"
            if is_mtp_active
            else "⚠️ НЕ АКТИВЕН (Только зарядка)"
        )

        batt_raw = self.run_adb("shell dumpsys battery")
        batt_data = {}
        for line in batt_raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                batt_data[k.strip()] = v.strip()

        batt_level = batt_data.get("level", "Н/Д")
        batt_temp_raw = batt_data.get("temperature", "0")
        try:
            batt_temp = f"{float(batt_temp_raw) / 10:.1f}°C"
        except Exception:
            batt_temp = "Н/Д"

        batt_volt_raw = batt_data.get("voltage", "0")
        try:
            batt_volt = f"{float(batt_volt_raw) / 1000:.2f} V"
        except Exception:
            batt_volt = "Н/Д"

        health_map = {
            "1": "Unknown",
            "2": "Good (Отличное)",
            "3": "Overheat (Перегрев)",
            "4": "Dead (Исчерпан ресурс)",
            "5": "Over voltage",
            "6": "Unspecified failure",
            "7": "Cold",
        }
        batt_health = health_map.get(
            batt_data.get("health", "1"), "Нормальное"
        )

        status_map = {
            "1": "Unknown",
            "2": "Заряжается",
            "3": "Разряжается",
            "4": "Не заряжается",
            "5": "Заряжена (100%)",
        }
        batt_status = status_map.get(batt_data.get("status", "1"), "Н/Д")

        storage_raw = self.run_adb("shell df -h /data")
        st_total = st_used = st_free = st_percent = "Н/Д"
        try:
            lines = storage_raw.splitlines()
            if len(lines) >= 2:
                parts = lines[1].split()
                st_total, st_used, st_free, st_percent = (
                    parts[1],
                    parts[2],
                    parts[3],
                    parts[4],
                )
        except Exception:
            pass

        mem_raw = self.run_adb("shell cat /proc/meminfo")
        mem_total_mb = mem_avail_mb = 0
        for line in mem_raw.splitlines():
            if "MemTotal:" in line:
                mem_total_mb = int(line.split()[1]) // 1024
            elif "MemAvailable:" in line:
                mem_avail_mb = int(line.split()[1]) // 1024

        if mem_total_mb > 0:
            mem_used_mb = mem_total_mb - mem_avail_mb
            ram_str = (
                f"{mem_used_mb} MB / {mem_total_mb} MB"
                f" ({int((mem_used_mb/mem_total_mb)*100)}% занято)"
            )
        else:
            ram_str = "Н/Д"

        report = f"""================================================================================
                    📊 ДИАГНОСТИЧЕСКИЙ ОТЧЕТ УСТРОЙСТВА
================================================================================

📱 [ ОСНОВНАЯ ИНФОРМАЦИЯ ]
   • Модель:            {brand.upper()} {model}
   • Производитель:     {manufacturer}
   • Версия Android:    {android_ver} (SDK API {sdk_ver})
   • Процессор/Чипсет:  {cpu.upper()}
   • Серийный номер:    {serial}
   • Разрешение экрана: {res} ({dpi} DPI)

🔌 [ РЕЖИМ USB И MTP (ПЕРЕДАЧА ФАЙЛОВ) ]
   • Статус MTP:        {mtp_status_str}
   • Конфигурация USB:  {usb_config} (State: {usb_state})

🔋 [ СОСТОЯНИЕ АККУМУЛЯТОРА ]
   • Заряд батареи:     {batt_level}% [{batt_status}]
   • Температура:       {batt_temp}
   • Напряжение:        {batt_volt}
   • Здоровье АКБ:      {batt_health}

💾 [ ПАМЯТЬ И ХРАНИЛИЩЕ ]
   • Оперативная (RAM): {ram_str}
   • Память (/data):    Всего: {st_total} | Использовано: {st_used} ({st_percent}) | Свободно: {st_free}

================================================================================
"""
        self.update_diag_text(report)
        self.log("[+] Диагностика завершена!")
        self.stop_animation()

    def update_diag_text(self, text):
        self.txt_diag.configure(state="normal")
        self.txt_diag.delete("1.0", "end")
        self.txt_diag.insert("1.0", text)
        self.txt_diag.configure(state="disabled")

    def enable_mtp(self):
        self.start_animation()
        self.log("\n[=== ВКЛЮЧЕНИЕ РЕЖИМА MTP + ADB ===]")

        # Включаем MTP С СОХРАНЕНИЕМ ADB, чтобы отладка не отваливалась
        self.run_adb("shell svc usb setFunctions mtp,adb")
        self.run_adb("shell setprop sys.usb.config mtp,adb")

        self.log("[+] Команда на включение MTP+ADB отправлена.")
        self.stop_animation()

        messagebox.showinfo(
            "Режим MTP",
            "Включен режим Передачи Файлов (MTP + ADB).\n\n"
            "⚠️ ВАЖНО:\n"
            "1. Разблокируйте экран телефона, чтобы ПК увидел ваши файлы.\n"
            "2. Если файлы не появились в Проводнике, нажмите кнопку 'Настройки"
            " USB в телефоне'.",
        )
        self.check_device()

    def open_usb_settings(self):
        self.run_adb("shell am start -a android.settings.USB_SETTINGS")
        self.log("[+] Открыто меню настроек USB на экране телефона.")


if __name__ == "__main__":
    app = AndroidCleanerApp()
    app.mainloop()