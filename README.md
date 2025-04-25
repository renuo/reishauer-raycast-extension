# Reishauer Menu Raycast Extension

This extension fetches the daily menu from the Reishauer staff restaurant API and displays it within Raycast.

## Features

- Fetches the current menu from the API (`http://localhost:5001/menu`).
- Displays menu items with names and prices in a list.
- Provides a detail view for each menu item, showing its description.

## Setup

1.  Ensure you are connected to the network where the API (`http://localhost:5001`) is accessible.
2.  Install the extension via the Raycast store (once published) or build it locally.

## Development

1.  Clone the repository.
2.  Go into `api` folder.
3.  Run `uv venv venv && source venv/bin/activate && uv pip install -r requirements.txt && uv run main.py`
4.  Open a new terminal.
5.  Run `pnpm install`.
6.  Run `pnpm dev` to start the development server.
7.  Add the extension to your Raycast extensions folder.

## Note

This extension relies on an internal API and will only work when connected to the API located in [`/api`](api).
