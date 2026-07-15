"""Open-Meteo forecast helpers."""

from __future__ import annotations

import datetime as dt
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from scoring import score_hour, label


@dataclass
class HourForecast:
    time: str
    wind_kmh: float
    gust_kmh: float
    wave_m: float
    rain_prob: float
    score: int

    @property
    def label(self) -> str:
        return label(self.score)


def fetch_json(url: str, params: dict[str, object]) -> dict:
    query = urllib.parse.urlencode(params)
    with urllib.request.urlopen(f"{url}?{query}", timeout=20) as response:
        return json.loads(response.read().decode())


def get_forecast(latitude: float, longitude: float, hours: int = 24) -> list[HourForecast]:
    weather = fetch_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "wind_speed_10m,wind_gusts_10m,precipitation_probability",
            "forecast_days": 2,
            "timezone": "auto",
        },
    )
    marine = fetch_json(
        "https://marine-api.open-meteo.com/v1/marine",
        {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "wave_height",
            "forecast_days": 2,
            "timezone": "auto",
        },
    )

    now = dt.datetime.now().replace(minute=0, second=0, microsecond=0)
    weather_hourly = weather["hourly"]
    marine_hourly = marine["hourly"]

    result: list[HourForecast] = []
    for idx, time_text in enumerate(weather_hourly["time"]):
        t = dt.datetime.fromisoformat(time_text)
        if t < now:
            continue
        if len(result) >= hours:
            break

        wave = 0.0
        if time_text in marine_hourly["time"]:
            marine_idx = marine_hourly["time"].index(time_text)
            wave = float(marine_hourly["wave_height"][marine_idx] or 0)

        wind = float(weather_hourly["wind_speed_10m"][idx] or 0)
        gust = float(weather_hourly["wind_gusts_10m"][idx] or 0)
        rain = float(weather_hourly["precipitation_probability"][idx] or 0)
        result.append(HourForecast(time_text, wind, gust, wave, rain, score_hour(wind, gust, wave, rain)))

    return result


def render_message(location_name: str, forecasts: list[HourForecast]) -> str:
    best = sorted(forecasts, key=lambda item: item.score, reverse=True)[:5]
    lines = [f"🌊 Sea SUP forecast - {location_name}", "", "Best hours:"]
    for item in best:
        hour = item.time.replace("T", " ")
        lines.append(
            f"• {hour} — {item.score}/100 ({item.label}) | wind {item.wind_kmh:.0f} km/h, "
            f"gust {item.gust_kmh:.0f} km/h, waves {item.wave_m:.2f} m, rain {item.rain_prob:.0f}%"
        )
    return "\n".join(lines)
