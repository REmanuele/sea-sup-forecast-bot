#!/usr/bin/env python3
"""Sea SUP Forecast Telegram Bot."""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from forecast import get_forecast, render_message


ENV_PATH = Path(__file__).with_name(".env")


def load_env(path: Path = ENV_PATH) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def telegram_request(token: str, method: str, payload: dict[str, object]) -> dict[str, object]:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(payload).encode()
    request = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


def send_message(token: str, chat_id: str, text: str) -> None:
    telegram_request(token, "sendMessage", {"chat_id": chat_id, "text": text})


def build_forecast_message(env: dict[str, str]) -> str:
    lat = float(env["LATITUDE"])
    lon = float(env["LONGITUDE"])
    name = env.get("LOCATION_NAME", "Configured location")
    forecasts = get_forecast(lat, lon, hours=24)
    return render_message(name, forecasts)


def main() -> int:
    env = {**load_env(), **os.environ}
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat_id = env.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")

    offset = 0
    send_message(token, chat_id, "🌊 Sea SUP Forecast Bot started. Use /mare for forecast.")

    while True:
        try:
            data = telegram_request(token, "getUpdates", {"timeout": 30, "offset": offset})
            for update in data.get("result", []):
                offset = int(update["update_id"]) + 1
                message = update.get("message", {})
                incoming_chat_id = str(message.get("chat", {}).get("id", ""))
                text = message.get("text", "")
                if incoming_chat_id != chat_id:
                    continue
                if text == "/mare":
                    send_message(token, chat_id, build_forecast_message(env))
        except Exception as exc:
            print(f"Bot error: {exc}")
            time.sleep(10)


if __name__ == "__main__":
    raise SystemExit(main())
