# Preview support

## Web

The workflow provides a local preview plan using `python -m http.server 8000` and `http://127.0.0.1:8000`.

## Jupyter

The workflow provides `jupyter lab` and `http://localhost:8888` as local preview metadata.

## App

The workflow provides `npx expo start --web` and `http://localhost:8081` as the expected Expo web preview. Actual Expo preview requires Node/npm/Expo dependencies in the environment.

These are preview plans, not hosted deployment URLs.
