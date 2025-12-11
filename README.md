# Koyso Game Scraper

A Python script to scrape games from [Koyso](https://koyso.to), view details, and retrieve final download links with optional automatic downloading.

---

## Features

* Scrape all games from Koyso with pagination support.
* Search games by title or keywords.
* Retrieve game details including title, description, file size, and cover image.
* Generate final download links using timestamp and secret key.
* Optional automatic downloading of selected games.
* Display game images and file size in console.

---

## Requirements

* Python 3.x
* Standard libraries: `urllib`, `re`, `json`, `html`, `hashlib`, `time`

---

## Usage

1. Run the script:

```bash
python koyso_scraper.py
```

2. Follow prompts:

* Enter a game name to search.
* Select a game from the search results.
* View details and final download link.
* Optionally, download the game automatically.

---

## Configuration Options

* `self.display_images` – Show game images in console (default: `True`)
* `self.show_file_size` – Display file size (default: `True`)
* `self.automatic_download` – Automatically download selected games (default: `True`)
* `self.request_delay` – Delay between requests in seconds (default: `0`)

---

## Methods Overview

* `get_all_games()` – Fetch all games from Koyso.
* `search_game(query)` – Search loaded games by title or keywords.
* `get_game_details(game_url)` – Fetch game details from a game page.
* `generate_hash(timestamp, game_id)` – Generate SHA256 hash for download request.
* `get_final_download_url(game_id)` – Get final downloadable URL.
* `download_file(url, filename)` – Download a file from a URL.

---

## Disclaimer

This script interacts with a third-party website. Use responsibly and ensure you comply with their terms of service. Unauthorized distribution or use may be illegal.