"""Run: python3 -m unittest -v test_forecast.py"""
import unittest
from unittest.mock import patch

import forecast


TIMES = ["2099-06-01T08:00", "2099-06-01T09:00", "2099-06-01T10:00"]


def weather(wind=(4, 6, 7), gust=(7, 10, 10), rain=(0, 10, 20)):
    return {"hourly": {"time": TIMES, "wind_speed_10m": wind,
                       "wind_gusts_10m": gust, "precipitation_probability": rain}}


def marine(times=TIMES, waves=(0.1, 0.2, 0.3)):
    return {"hourly": {"time": times, "wave_height": waves}}


class ForecastTests(unittest.TestCase):
    @patch("forecast.fetch_json")
    def test_weather_and_marine_are_requested_in_utc(self, mock_fetch):
        mock_fetch.side_effect = [weather(), marine()]
        forecasts = forecast.get_forecast(37.0, 15.0)
        self.assertEqual(len(forecasts), 3)
        self.assertEqual(mock_fetch.call_args_list[0].args[1]["timezone"], "UTC")
        self.assertEqual(mock_fetch.call_args_list[1].args[1]["timezone"], "UTC")

    @patch("forecast.fetch_json")
    def test_missing_marine_hour_is_excluded_not_treated_as_calm(self, mock_fetch):
        mock_fetch.side_effect = [weather(), marine(times=[TIMES[0], TIMES[2]], waves=[0.1, 0.3])]
        result = forecast.get_forecast(37.0, 15.0)
        self.assertEqual([x.time for x in result], [TIMES[0], TIMES[2]])

    @patch("forecast.fetch_json")
    def test_missing_wave_value_is_excluded(self, mock_fetch):
        mock_fetch.side_effect = [weather(), marine(waves=[0.1, None, 0.3])]
        result = forecast.get_forecast(37.0, 15.0)
        self.assertEqual(len(result), 2)

    @patch("forecast.fetch_json")
    def test_zero_wave_as_actual_measurement_is_valid(self, mock_fetch):
        mock_fetch.side_effect = [weather(), marine(waves=[0.0, 0.2, 0.3])]
        result = forecast.get_forecast(37.0, 15.0)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].wave_m, 0)

    @patch("forecast.fetch_json")
    def test_missing_or_invalid_weather_is_excluded(self, mock_fetch):
        mock_fetch.side_effect = [weather(wind=[4, None, 7], rain=[0, 0, 101]), marine()]
        result = forecast.get_forecast(37.0, 15.0)
        self.assertEqual(len(result), 1)

    def test_no_forecast_has_explicit_warning(self):
        message = forecast.render_message("Test location", [])
        self.assertIn("No complete hourly forecast", message)
        self.assertIn("must not be interpreted as calm", message)

    @patch("forecast.fetch_json")
    def test_report_labels_utc_hours(self, mock_fetch):
        mock_fetch.side_effect = [weather(), marine()]
        message = forecast.render_message("Test", forecast.get_forecast(37, 15))
        self.assertIn("UTC", message)
        self.assertIn("Only hours with complete inputs", message)

    def test_invalid_number_rejected(self):
        for value in (None, -1, "NaN", "inf", "bad", True):
            with self.subTest(value=value):
                self.assertIsNone(forecast._valid_number(value))


if __name__ == "__main__":
    unittest.main()
