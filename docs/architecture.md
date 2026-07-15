# Architecture

The Sea SUP Forecast Bot is designed as a lightweight Telegram assistant deployed on a Raspberry Pi.

## Main components

- Telegram bot interface
- Weather forecast data source
- Marine forecast data source
- Custom scoring model
- Daily scheduled report
- On-demand `/mare` command
- Optional webcam integration
- systemd service for automatic startup

## Data flow

1. The bot receives a scheduled trigger or a Telegram command.
2. Weather and marine forecast data are retrieved.
3. Conditions are normalized into hourly values.
4. A custom score is calculated for each hour.
5. The best time window is selected.
6. A readable Telegram report is generated.
