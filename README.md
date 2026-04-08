# NextToppers Telegram Key Bot

## Setup Steps

### 1. Create Telegram Bot
- Open Telegram → search @BotFather
- Send `/newbot` → follow steps → copy the BOT_TOKEN
- Paste it in `bot.py` → `BOT_TOKEN = "..."`

### 2. Get your Telegram User ID
- Search @userinfobot on Telegram → send any message → copy your ID
- Paste in `bot.py` → `ADMIN_IDS = [YOUR_ID]`

### 3. Firebase Service Account Key
- Firebase Console → Project Settings → Service Accounts
- Click "Generate new private key" → download JSON
- Rename it to `serviceAccountKey.json` → place in this folder

### 4. Install & Run
```bash
pip install -r requirements.txt
python bot.py
```

## How it works

| Step | What happens |
|------|-------------|
| Admin sends `/genkey` | Bot generates `NT-XXXXXXXX` key, saves to `_app_keys` in Firebase |
| Student enters key in app | App checks `_app_keys` collection |
| Key found & unused | Marked as used, `expiresAt` = now + 24hrs, access granted |
| Key found & within 24hrs | Access granted directly |
| Key expired or not found | "Invalid Key" shown |

## Firebase Structure (_app_keys)

```
_app_keys/
  NT-A3F9K2XP/
    key: "NT-A3F9K2XP"
    isUsed: false
    createdAt: timestamp
    createdBy: "telegram_user_id"
    expiresAt: null  ← set when first used
    usedAt: null     ← set when first used
```
