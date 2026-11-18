import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile

from config import CURRENT_OS

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

    # 2. Переменная окружения Android SDK
    android_sdk = os.environ.get("ANDROID_SDK_ROOT") or os.environ.get("ANDROID_HOME")
    if android_sdk:
        sdk_adb = os.path.join(android_sdk, "platform-tools", adb_exe)
        if os.path.exists(sdk_adb):
            return sdk_adb

    # 3. Локальный абсолютный путь C:\cleaner_android\adb
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
