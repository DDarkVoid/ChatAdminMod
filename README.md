# ChatAdminMod

Telegram Business chatbot for chat moderation.

ChatAdminMod is a Python-based Telegram bot designed to provide moderation features for Telegram Business chats.

## Features

*  Mute and unmute users
*  Temporary and permanent mutes
*  Anti-spam protection
*  Automatic deletion of messages from muted users
*  Telegram Business Connection support
*  Business connection permission checking
*  SQLite database
*  Basic service tests
*  Environment-based configuration

## Project Structure

```text
ChatAdminMod/
├── app/
│   ├── database/
│   ├── handlers/
│   ├── services/
│   └── utils/
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── test_mute_service.py
```

## Requirements

* Python 3.10+
* A Telegram bot
* Required Telegram bot permissions for moderation features
* Telegram Business features for Business Connection functionality

## Installation

Clone the repository:

```bash
git clone https://github.com/DDarkVoid/ChatAdminMod.git
cd ChatAdminMod
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root.

You can use `.env.example` as a template:

```env
BOT_TOKEN=your_bot_token_here
```

Replace `your_bot_token_here` with your Telegram bot token.

**Never commit your `.env` file or bot token to Git.**

The repository already contains a `.gitignore` rule for `.env`.

## Running

Start the bot with:

```bash
python main.py
```

The bot will start polling Telegram updates.

## Testing

Run the mute service tests with:

```bash
python test_mute_service.py
```

## Database

ChatAdminMod uses SQLite for persistent data.

The database is created automatically when the application runs.

Database files are intentionally excluded from Git using `.gitignore`.

## Security

Do not publish:

* `.env`
* Telegram bot tokens
* SQLite database files
* private credentials
* production configuration

Only `.env.example` should be committed as an example configuration.

## Status

The project is under active development.

Features and internal architecture may change as the project evolves.

## License

No open-source license has been added yet.
