# WhatsApp AI Agent

A personal AI assistant that lives inside WhatsApp. Send it a text or voice note and it replies intelligently — it can read your emails, manage your calendar, and search the web, all without leaving WhatsApp.

## Demo

> "Read my latest emails" → agent reads your Gmail and summarizes them
> "Do I have anything tomorrow?" → agent checks your Google Calendar
> "Add a meeting on April 5 at 3pm" → agent creates the event
> "What's the latest news about AI?" → agent searches the web and replies
> Send a voice note → agent understands it and replies with a voice note

## Features

- **Text & Voice** — send text or voice notes, get replies in both formats
- **Gmail** — read emails, send emails on your behalf
- **Google Calendar** — read, create, update, and delete events
- **Web Search** — real-time search via DuckDuckGo (no API key needed)
- **Memory** — remembers your past conversations (SQLite)
- **Auto-reconnect** — stays connected even if WhatsApp session drops

## Tech Stack

| Layer | Tool |
|---|---|
| WhatsApp interface | whatsapp-web.js (Node.js) |
| AI brain | Groq LLaMA 3 (free tier) |
| Speech-to-text | Groq Whisper |
| Text-to-speech | Microsoft Edge TTS |
| Gmail + Calendar | Google APIs |
| Web search | DuckDuckGo |
| Memory | SQLite |
| Backend | Python + Flask |

## Setup

### Requirements
- Node.js v18+
- Python 3.10+
- ffmpeg (in PATH)

### 1. Clone the repo
```bash
git clone https://github.com/mnatafgi03/whatsapp-ai-agent.git
cd whatsapp-ai-agent
```

### 2. Install Python dependencies
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Install Node.js dependencies
```bash
cd ../whatsapp
set PUPPETEER_SKIP_DOWNLOAD=true   # Windows
npm install
```

### 4. Set up environment variables
Create `backend/.env`:
```
GROQ_API_KEY=your_groq_api_key
```
Get a free Groq API key at [console.groq.com](https://console.groq.com)

### 5. Set up Google APIs (Gmail + Calendar)
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project, enable Gmail API and Google Calendar API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download as `backend/credentials.json`
5. Add your Gmail as a test user in OAuth consent screen

### 6. Run
```bash
# Start both services
start.bat
```
Or manually:
```bash
# Terminal 1
cd backend && venv\Scripts\activate && python main.py

# Terminal 2
cd whatsapp && node index.js
```

Scan the QR code with WhatsApp → **Settings → Linked Devices → Link a Device**

## Project Structure
```
whatsapp-agent/
├── backend/
│   ├── main.py          # Flask server
│   ├── agent.py         # AI brain + tool calling
│   ├── memory.py        # SQLite conversation memory
│   ├── stt.py           # Speech to text (Groq Whisper)
│   ├── tts.py           # Text to speech (Edge TTS)
│   └── tools/
│       ├── gmail.py     # Gmail read/send
│       ├── calendar.py  # Calendar CRUD
│       └── search.py    # Web search
└── whatsapp/
    └── index.js         # WhatsApp interface
```

## Built by
Mohamad Natafgi — [LinkedIn](https://linkedin.com/in/mnatafgi/) | [GitHub](https://github.com/mnatafgi03)
