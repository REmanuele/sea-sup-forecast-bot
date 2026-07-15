# Sea SUP Forecast Bot

Telegram bot that analyzes weather and marine forecast data to suggest the best time window for SUP activities.

## Why I built it

For sea activities such as SUP, the best time depends on multiple conditions: wind, gusts, waves and rain probability. This bot automates the daily forecast and ranks the best hours.

## Features

- Daily or on-demand forecast
- `/mare` command
- 24-hour analysis
- Best-hour ranking
- Wind, gusts, wave height and rain probability
- Configurable location
- Raspberry Pi deployment with systemd
- No external Python dependencies

## Tech stack

- Python 3
- Telegram Bot API
- Open-Meteo Forecast API
- Open-Meteo Marine API
- Raspberry Pi
- systemd

## Setup

```bash
git clone https://github.com/REmanuele/sea-sup-forecast-bot.git
cd sea-sup-forecast-bot
cp .env.example .env
nano .env
python3 bot.py
```

## Example command

```text
/mare
```

## Safety

Never commit tokens, chat IDs or private configuration files.

## Real-world case study

This project was designed as a real Telegram assistant for daily sea-condition evaluation.

The bot combines weather forecast, marine forecast and a custom scoring model to suggest the best time window for SUP activities.

The system was deployed on a Raspberry Pi using systemd and supports both scheduled daily reports and on-demand forecast requests.
