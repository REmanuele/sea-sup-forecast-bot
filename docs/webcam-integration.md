# Webcam Integration

The project can optionally include a webcam snapshot as a visual support for the forecast.

## Purpose

Forecast data is useful, but a live visual check can help validate the real sea conditions.

## Possible approach

- Open a public webcam page
- Capture a screenshot or video frame
- Crop the relevant sea area
- Send the image after the forecast message

## Technical notes

A browser automation tool such as Selenium can be used when a direct static image URL is not available.

## Safety and privacy

Only public webcam sources should be used. Private cameras, credentials or restricted URLs must not be committed.
