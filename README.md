![Vyla Game Scraper Logo](/images/github-banner.jpg)

# Vyla Game Scraper

A Python script to scrape games from [Vyla](https://koyso.to), view details, and retrieve final download links with optional automatic downloading. Now also includes a dynamic frontend HTML interface.


## Features

* Scrape all games from Vyla with pagination support.
* Search games by title or keywords.
* Retrieve game details including title, description, file size, and cover image.
* Generate final download links using timestamp and secret key.
* Optional automatic downloading of selected games.
* Display game images and file size in console.
* Dynamic web interface to browse games, view overlays with details, and download files.


## Requirements

* Python 3.x
* Standard libraries: `urllib`, `re`, `json`, `html`, `hashlib`, `time`
* Optional: A lightweight backend server for the web interface (e.g., Flask or FastAPI)


## Usage

### Python Script

1. Run the script:

```bash
python Vyla_scraper.py
````

2. Follow prompts:

* Select a genre.
* Enter a game name to search.
* Select a game from the search results.
* View details and final download link.
* Optionally, download the game automatically.

### Web Interface

1. Serve the provided `index.html` via a local server.
2. Implement backend endpoints:

   * `/api/games?genre=X&page=Y` – Returns JSON of games for the selected genre and page.
   * `/api/game_details?id=Z` – Returns JSON of game details (title, description, file size, cover image, download link).
3. Open `index.html` in a browser to dynamically browse, view overlays, and access download links.


## Configuration Options

* `self.display_images` – Show game images in console (default: `True`)
* `self.show_file_size` – Display file size (default: `True`)
* `self.automatic_download` – Automatically download selected games (default: `False`)
* `self.request_delay` – Delay between requests in seconds (default: `0.05`)


## Methods Overview

* `get_all_games(genre_id=None)` – Fetch all games or by specific genre.
* `search_game(query)` – Search loaded games by title or keywords.
* `get_game_details(game_url)` – Fetch game details from a game page.
* `generate_hash(timestamp, game_id)` – Generate SHA256 hash for download request.
* `get_final_download_url(game_id)` – Get final downloadable URL.
* `download_file(url, filename)` – Download a file from a URL.


## Disclaimer

This script interacts with a third-party website. Use responsibly and ensure you comply with their terms of service. Unauthorized distribution or use may be illegal.