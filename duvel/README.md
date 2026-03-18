# Duvel Build Agent

A Telegram bot that updates module revisions in a platform YAML file and triggers a build pipeline.

## What it does

- Listens for `/build` commands in Telegram.
- Updates these module revisions in `platform.yaml`:
  - `mdep-devicesetupwizard-extra-screens`
  - `mdep-devicesetupwizard-apk`
- Runs the build script.
- Checks `build.log` for a success signature and sends the result back to Telegram.

## Repository structure

```text
.
└── build_agent.py
```

## Requirements

- Python 3.9+
- A Telegram bot token
- Access to the build environment paths used by the script

Python packages:

- `pyTelegramBotAPI` (imported as `telebot`)
- `ruamel.yaml`

Install dependencies:

```bash
pip install pyTelegramBotAPI ruamel.yaml
```

## Configuration

Set these environment variables before running:

- `TELEGRAM_BOT_TOKEN` (required)
- `ALLOWED_USER_ID` (optional, restricts who can trigger builds)

Example:

```bash
export TELEGRAM_BOT_TOKEN="<your-bot-token>"
export ALLOWED_USER_ID="123456789"
```

## Important paths in `build_agent.py`

The script currently uses hardcoded Jenkins/local paths:

- `YAML_PATH=/home/jenkins/Work/mybuild/wave4-platform-builder/platforms/w4duvel/platform.yaml`
- `BUILD_CWD=/home/jenkins/Work/mybuild/wave4-platform-builder`
- `BUILD_CMD=bash platforms/w4duvel/run.sh 2>&1 | tee build.log`
- `LOG_FILE=<BUILD_CWD>/build.log`

Update these constants if your environment differs.

## Usage

Run the agent:

```bash
python build_agent.py
```

In Telegram, send:

```text
/build [extra-rev] [apk-rev]
```

Example:

```text
/build 1.2.3 4.5.6
```

## Build result detection

A build is treated as successful when `build.log` contains:

```text
Fetching signed w4duvel_ota tar file
```

If not found, the bot reports failure.

## Security notes

- Keep `TELEGRAM_BOT_TOKEN` secret.
- Use `ALLOWED_USER_ID` to prevent unauthorized build triggers.
- Run this bot only in trusted environments since it executes shell commands.

## Troubleshooting

- **`No TELEGRAM_BOT_TOKEN found`**: set `TELEGRAM_BOT_TOKEN` in your environment.
- **`Unauthorized`**: verify `ALLOWED_USER_ID` matches your Telegram user ID.
- **`Targets not found`**: confirm the module names exist in the YAML file.
- **`build.log not found`**: verify `BUILD_CWD` and `BUILD_CMD` are correct.

## License

Add your preferred license (for example, MIT) to this repository.
