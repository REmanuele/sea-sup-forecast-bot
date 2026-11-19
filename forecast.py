"""Open-Meteo helpers: never treat missing marine or weather data as calm conditions."""

from __future__ import annotations

import datetime as dt
import json
import math
import urllib.parse
import urllib.request
from dataclasses import dataclass
from scoring import score_hour, label


@dataclass
class HourForecast:
    time: str  # UTC ISO 8601; displayed with an explicit UTC label
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


def _valid_number(value: object, *, upper_limit: float | None = None) -> float | None:
    """None/invalid/negative measurements are unknown, never zero."""
    try:
        if value is None or isinstance(value, bool):
            return None
        result = float(value)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(result) or result < 0 or (upper_limit is not None and result > upper_limit):
        return None
    return result


def _utc_time(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    # Open-Meteo's timezone=UTC response uses naive UTC timestamps.
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def get_forecast(latitude: float, longitude: float, hours: int = 24) -> list[HourForecast]:
    if hours <= 0:
        return []
    weather = fetch_json("https://api.open-meteo.com/v1/forecast", {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "wind_speed_10m,wind_gusts_10m,precipitation_probability",
        "forecast_days": 2,
        "timezone": "UTC",
    })
    marine = fetch_json("https://marine-api.open-meteo.com/v1/marine", {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "wave_height",
        "forecast_days": 2,
        "timezone": "UTC",
    })

    weather_hourly = weather["hourly"]
    marine_hourly = marine["hourly"]
    wave_by_time = dict(zip(marine_hourly["time"], marine_hourly["wave_height"]))
    now = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    result: list[HourForecast] = []
    for time_text, wind_raw, gust_raw, rain_raw in zip(
        weather_hourly["time"],
        weather_hourly["wind_speed_10m"],
        weather_hourly["wind_gusts_10m"],
        weather_hourly["precipitation_probability"],
    ):
        instant = _utc_time(time_text)
        if instant < now:
            continue
        if len(result) >= hours:
            break
        # A zero-wave measurement is valid; a missing time/value is NOT zero.
        wave = _valid_number(wave_by_time.get(time_text))
        wind = _valid_number(wind_raw)
        gust = _valid_number(gust_raw)
        rain = _valid_number(rain_raw, upper_limit=100)
        if any(item is None for item in (wave, wind, gust, rain)):
            continue
        result.append(HourForecast(
            instant.strftime("%Y-%m-%dT%H:%M"),
            wind, gust, wave, rain, score_hour(wind, gust, wave, rain)
        ))
    return result


def render_message(location_name: str, forecasts: list[HourForecast]) -> str:
    heading = f"Sea SUP forecast — {location_name}"
    if not forecasts:
        return (f"{heading}\n\nNo complete hourly forecast is available. "
                "Missing wave or weather data must not be interpreted as calm conditions. "
                "Check local official forecasts and warnings before going out.")
    best = sorted(forecasts, key=lambda item: item.score, reverse=True)[:5]
    lines = [heading, "", "Highest-rated complete hours (UTC):"]
    for item in best:
        hour = item.time.replace("T", " ")
        lines.append(
            f"• {hour} UTC — {item.score}/100 ({item.label}) | "
            f"wind {item.wind_kmh:.0f} km/h, gust {item.gust_kmh:.0f} km/h, "
            f"waves {item.wave_m:.2f} m, rain {item.rain_prob:.0f}%"
        )
    lines.extend(["", "Only hours with complete inputs are ranked.",
                  "Informational model only: verify official local forecasts and sea warnings before SUP."])
    return "\n".join(lines)
