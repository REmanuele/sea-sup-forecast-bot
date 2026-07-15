# Raspberry Pi Deployment

The bot is designed to run on a Raspberry Pi or a small Linux server.

## Deployment approach

- Python virtual environment
- Environment variables stored in .env
- systemd service for automatic startup
- Journal logs for troubleshooting

## Example systemd workflow

1. Copy the service file into the systemd directory.
2. Reload systemd.
3. Enable the service at boot.
4. Start the service.
5. Read logs with journalctl.

## Commands

```bash
sudo cp systemd/sea-sup-forecast-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sea-sup-forecast-bot
sudo systemctl start sea-sup-forecast-bot
sudo journalctl -u sea-sup-forecast-bot -f
```

## Notes

Real bot tokens, chat IDs and private configuration files must never be committed to the repository.
