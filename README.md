# CopyStickerBot

Telegram bot for creating and managing sticker packs.  
Built with [aiogram 3.x](https://docs.aiogram.dev).

---

## 🚀 Installation (Windows)

1. Clone the repository:

```powershell
git clone https://github.com/username/CopyStickerBot.git
cd CopyStickerBot
```

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```powershell
pip install -r requirements.pip
```

4. Create a `.env` file in the project root:

```env
BOT_TOKEN=your_telegram_bot_token
```

---

## 🔥 Run in development mode with hot-reload

To automatically restart the bot whenever any `.py` or `.env` file changes:

```powershell
watchmedo auto-restart --pattern="*.py;*.env" --recursive -- .venv\Scripts\python.exe src\bot.py
```

- `--pattern="*.py;*.env"` – watches both Python files and the environment file  
- `--recursive` – watches all subdirectories (e.g. `src/handlers/`)  
- `.venv\Scripts\python.exe` – ensures the bot runs with the virtual environment Python  

---

## 🛑 Run without hot-reload

```powershell
python src\bot.py
```

---

## ⚠️ Notes

- If you see `TelegramConflictError: terminated by other getUpdates request`, it means multiple instances of the bot are running with the same token. Make sure only one process is active.  
- On Windows, always use `.venv\Scripts\python.exe` inside `watchmedo` to avoid using the system Python without dependencies.  
- To stop the bot, press `Ctrl+C` in the terminal.  

---
