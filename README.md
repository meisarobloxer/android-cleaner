# 📱 Android Cleaner

**Android Cleaner** — это удобное и современное десктопное приложение для диагностики, оптимизации и очистки устройств на базе Android с использованием подключений ADB и MTP.

---

## ✨ Основные возможности

* 🔍 **Полная диагностика:** Проверка системного состояния устройства через ADB и MTP.
* 🧹 **Очистка памяти:** Поиск и удаление неиспользуемых файлов, кеша и мусора.
* 💻 **Кроссплатформенность:** Готовые сборки для **Windows** (`.exe`) и **macOS** (`.app`).
* 🎨 **Современный UI:** Удобный графический интерфейс на базе `CustomTkinter`.

---

## 🚀 Быстрый старт

### Запуск из исходного кода

1. Клонируйте репозиторий:
   ```bash
   git clone [https://github.com/meisarobloxer/Android-Cleaner.git](https://github.com/meisarobloxer/Android-Cleaner.git)
   cd Android-Cleaner
Установите необходимые зависимости:

Bash
pip install -r requirements.txt
Запустите приложение:

Bash
python main.py
🛠 Сборка автономного приложения
Для создания готового исполняемого файла используйте PyInstaller:

Windows (.exe):

Bash
pyinstaller --noconfirm --onedir --windowed --add-data "assets;assets/" main.py
macOS (.app):

Bash
pyinstaller --noconfirm --onedir --windowed --add-data "assets:assets" main.py
🌐 Социальные сети
Следите за обновлениями и новыми версиями проекта:

TikTok: @android_cleaner

Instagram: @android_cleaner_github

📜 Лицензия
Проект распространяется под лицензией MIT.