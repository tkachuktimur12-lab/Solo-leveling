# Solo Leveling

Telegram Mini App (and bot) inspired by Solo Leveling progression systems — a fitness gamification RPG.

## Features
- **Daily Quests**: 5 random fitness exercises, earn XP and streaks
- **Dungeons**: E→S ranked dungeon gates with enemy tasks and boss fights
- **Class System**: Awakening (level 10) and Job Change (level 100)
- **Equipment**: Loot, inventory, and equipment with rarity tiers
- **Stat Allocation**: STR / INT / AGI / VIT / SENSE
- **Hidden & Dungeon Rolls**: Chance-based bonus quests and high-rank dungeons

## Structure
- `game/` — shared game logic (constants, DB, calculations)
- `api/` — FastAPI backend (REST API for the Mini App)
- `webapp/` — React Mini App (Vite + TypeScript + Mantine UI)
- `bot/` — original Telegram bot (kept for reference)

## Run the Mini App

### 1. Backend (FastAPI)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure token
cp .env.example .env
# Set TELEGRAM_BOT_TOKEN=your_token_here

# Start the API server
uvicorn api.main:app --reload --port 8000
```

### 2. Frontend (React)
```bash
cd webapp
npm install
npm run dev
```

The dev server proxies `/api` requests to `http://localhost:8000`.

### 3. Connect to Telegram
1. Open [@BotFather](https://t.me/BotFather)
2. Go to **Bot Settings → Configure Mini App → Edit Mini App URL**
3. Set the URL to your deployed frontend (e.g. your HTTPS tunnel or hosting URL)

## Run the Bot (legacy)
```bash
pip install -r requirements.txt
cp .env.example .env
# Set TELEGRAM_BOT_TOKEN=your_token_here
python main.py
```

## Tech Stack
- **Backend**: Python, FastAPI, SQLite
- **Frontend**: React 18, Vite, TypeScript, Mantine v7
- **Telegram**: @telegram-apps/sdk-react, telegram-init-data
