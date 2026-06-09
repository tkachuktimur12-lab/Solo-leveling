# Solo-leveling
Telegram bot concept inspired by Solo Leveling progression systems.

## Structure
- `main.py`: lightweight entrypoint
- `bot/config.py`: runtime config and token loading
- `bot/constants.py`: static game data (quests, dungeons, shop)
- `bot/db.py`: SQLite schema and user/equipment persistence
- `bot/game_logic.py`: pure game helpers and calculations
- `bot/handlers.py`: Telegram command + callback handlers
- `bot/app.py`: app wiring and handler registration

## Run
1. Set your bot token:
   - PowerShell: `$env:TELEGRAM_BOT_TOKEN="your_token_here"`
2. Start:
   - `python main.py`
