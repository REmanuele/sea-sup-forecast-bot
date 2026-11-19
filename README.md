# Sea SUP Forecast Bot

Telegram bot that combines Open-Meteo weather and marine forecasts into a **simple informational SUP conditions score**. It is an experimental personal project, **not a maritime safety service**.

## Current documented behavior

- Responds to `/mare` messages from a configured Telegram chat.
- Compares wind, gusts, wave height and precipitation probability over upcoming hours.
- Excludes an hour if any scoring input is missing or invalid; unknown wave height is never treated as 0 m.
- Uses **UTC** for both weather and marine forecasts to avoid comparing API-local times to the Raspberry Pi/server's timezone. Displayed times are clearly marked UTC. Convert to your local timezone before planning.
- Uses Python standard library; deployable as a script with a systemd unit example in the existing repository.

> The original README mentioned scheduled daily reports. The supplied `bot.py` currently implements a startup notification and on-demand `/mare` handling, but **does not itself implement daily scheduling**. Do not claim daily scheduling until that behavior is implemented and tested.

## Setup

```sh
cp .env.example .env
# Edit .env: Telegram token, allowed chat ID and coordinates
python3 bot.py
```

Keep real tokens/chat IDs out of Git, logs and shared screenshots.

## Run offline tests

```sh
python3 -m unittest -v test_forecast.py
```

These tests use mock API responses; they verify time alignment, missing input exclusion and warning text. They do not validate forecast accuracy or seaworthiness.

## Safety and technical limitations

- The score is an unvalidated heuristic, not a risk assessment or go/no-go decision.
- Missing marine coverage means **no rating** for that hour, not safe sea conditions.
- Forecast errors, rapidly changing conditions, currents, offshore wind, visibility, coastal geography and local warnings are not fully represented.
- Consult official local weather/marine forecasts, warnings and observed conditions before activities on the water.
- Python/API calls can fail; the existing bot loop logs exceptions and retries after a delay. Improve API error reporting and backoff before relying on unattended use.
