import urllib.request
import urllib.parse
import re
import json
import html
import hashlib
import time
import urllib.error


class KoysoScraper:

    def __init__(self):
        self.base_url = "https://koyso.to"
        self.all_games = []
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [
            ('User-Agent',
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            ('Accept',
             'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
             ),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Connection', 'keep-alive'),
            ('Upgrade-Insecure-Requests', '1'),
        ]
        self.genres = {
            '1': ('All Games', '/'),
            '2': ('Action Games', '/category/action'),
            '3': ('Adventure Games', '/category/adventure'),
            '4': ('R18+', '/category/r18'),
            '5': ('Shooting Games', '/category/shooting'),
            '6': ('Casual Games', '/category/casual'),
            '7': ('Sports Racing', '/category/sports_racing'),
            '8': ('Simulation Business', '/category/simulation'),
            '9': ('Role Playing', '/category/rpg'),
            '10': ('Strategy Games', '/category/strategy'),
            '11': ('Fighting Games', '/category/fighting'),
            '12': ('Horror Games', '/category/horror'),
            '13': ('Real-time strategy', '/category/rts'),
            '14': ('Card Game', '/category/card'),
            '15': ('Indie Games', '/category/indie'),
            '16': ('LAN connection', '/category/lan'),
            '17': ('Search Games', '/?keywords=')
        }
        self.secret_key = "f6i6@m29r3fwi^yqd"
        self.request_delay = 0.05    
        self.display_images = True
        self.show_file_size = True
        self.automatic_download = False

    def fetch_page(self, url):
        try:
            time.sleep(self.request_delay)
            request = urllib.request.Request(url)
            response = self.opener.open(request)
            content = response.read()
            return content.decode('utf-8')
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code} fetching {url}")
            if e.code == 403:
                print("Error 403: Access forbidden.")
            elif e.code == 404:
                print("Error 404: Page not found.")
            elif e.code == 429:
                print("Error 429: Too many requests. Try again later.")
            return ""
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def get_all_games(self, genre_id=None):
        self.all_games = []
        
        if genre_id and genre_id in self.genres:
            genre_name, genre_url = self.genres[genre_id]
            base_url = f"{self.base_url}{genre_url}"
            print(f"Fetching {genre_name} games...")
            self._scrape_genre_pages(base_url, genre_name)
        else:
            page = 1
            while True:
                url = f"{self.base_url}/?page={page}"
                print(f"Fetching all games page {page}...")
                html_content = self.fetch_page(url)
                if not html_content:
                    break

                games_found = self._extract_games_from_page(html_content)

                if games_found == 0:
                    print("No more games found.")
                    break

                print(f"Found {games_found} games on page {page}")
                page += 1

        print(f"Total games found: {len(self.all_games)}")
        return self.all_games

    def get_all_games_search(self, base_url, search_term):
        self.all_games = []
        page = 1
        
        while True:
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}&page={page}"
            
            print(f"Fetching search results page {page} for '{search_term}'...")
            html_content = self.fetch_page(url)
            
            if not html_content:
                break

            games_found = self._extract_games_from_page(html_content)
            
            if games_found == 0:
                print(f"No more games found for '{search_term}'.")
                break
                
            print(f"Found {games_found} games on page {page}")
            
            if not self._has_next_page(html_content, page):
                break
                
            page += 1
    
    def _scrape_genre_pages(self, base_url, genre_name):
        page = 1
        while True:
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}?page={page}"
            
            print(f"Fetching {genre_name} page {page}...")
            html_content = self.fetch_page(url)
            
            if not html_content:
                break

            games_found = self._extract_games_from_page(html_content)
            
            if games_found == 0:
                print(f"No more games found in {genre_name}.")
                break
                
            print(f"Found {games_found} games on page {page}")
            
            if not self._has_next_page(html_content, page):
                break
                
            page += 1

    def _has_next_page(self, html_content, current_page):
        next_page_pattern = r'<a[^>]*href="[^"]*\?page={}"[^>]*>'.format(current_page + 1)
        next_arrow_pattern = r'<a[^>]*href="[^"]*\?page={}"[^>]*class="anticon"[^>]*>'.format(current_page + 1)
        
        if re.search(next_page_pattern, html_content) or re.search(next_arrow_pattern, html_content):
            return True
        
        pagination_text = re.search(r'<a>(\d+)/(\d+)</a>', html_content)
        if pagination_text:
            current, total = pagination_text.groups()
            if int(current) < int(total):
                return True
        
        return False

    def _extract_games_from_page(self, html_content):
        games_found = 0
        game_item_pattern = r'<a class="game_item"[^>]*href="([^"]*)"[^>]*>.*?<img[^>]*(?:data-src|src)="([^"]*)"[^>]*>.*?<span[^>]*>([^<]*)</span>'
        game_item_matches = re.findall(game_item_pattern, html_content, re.DOTALL)

        if not game_item_matches:
            return 0

        for game_url, image_url, game_title in game_item_matches:
            game = {
                'title': html.unescape(game_title.strip()),
                'url': urllib.parse.urljoin(self.base_url, game_url.strip()),
                'id': game_url.strip().split('/')[-1],
                'image_url': image_url
            }
            if game not in self.all_games:
                self.all_games.append(game)
                games_found += 1

        return games_found

    def search_game(self, query):
        results = []
        query_lower = query.lower().strip()
        
        if not query_lower:
            return results
            
        search_terms = []
        if "gta" in query_lower:
            search_terms = ["grand theft auto", "gta"]
        elif " " in query_lower:
            search_terms = query_lower.split()
        else:
            search_terms = [query_lower]
        
        for game in self.all_games:
            title_lower = game['title'].lower()
            
            for term in search_terms:
                if term in title_lower:
                    if game not in results:
                        results.append(game)
                    break
        
        return results

    def get_game_details(self, game_url):
        html_content = self.fetch_page(game_url)
        if not html_content:
            return {'error': 'Failed to fetch page'}

        details = {}

        title_match = re.search(r'<h1 class="content_title"[^>]*>(.*?)</h1>',
                                html_content, re.DOTALL)
        if title_match:
            details['title'] = html.unescape(
                re.sub(r'<[^>]*>', '', title_match.group(1)).strip())

        description_match = re.search(
            r'<div class="content_body">.*?<p>(.*?)</p>', html_content,
            re.DOTALL)
        if description_match:
            details['description'] = html.unescape(
                re.sub(r'<[^>]*>', '', description_match.group(1)).strip())

        image_match = re.search(
            r'<div class="capsule_div">.*?<img[^>]*src="([^"]*)"',
            html_content, re.DOTALL)
        if image_match:
            details['image_url'] = image_match.group(1)

        size_match = re.search(r'<span>Size</span>\s*<span>([^<]+)</span>',
                               html_content)
        if size_match:
            details['file_size'] = size_match.group(1).strip()

        download_match = re.search(
            r'onclick="download\(\)".*?href="/download/(\d+)"', html_content,
            re.DOTALL)
        if download_match:
            details['game_id'] = download_match.group(1)
            details[
                'download_page'] = f"{self.base_url}/download/{download_match.group(1)}"
        else:
            download_match = re.search(
                r'<button[^>]*onclick="[^"]*/download/(\d+)[^"]*"',
                html_content)
            if download_match:
                details['game_id'] = download_match.group(1)
                details[
                    'download_page'] = f"{self.base_url}/download/{download_match.group(1)}"

        return details

    def generate_hash(self, timestamp, game_id):
        data = timestamp + game_id + self.secret_key
        return hashlib.sha256(data.encode()).hexdigest()

    def get_canvas_fingerprint(self):
        return 123456789

    def get_final_download_url(self, game_id):
        download_page_url = f"{self.base_url}/download/{game_id}"
        html_content = self.fetch_page(download_page_url)
        if not html_content:
            return None

        timestamp = str(int(time.time()))
        secret_hash = self.generate_hash(timestamp, game_id)
        canvas_id = self.get_canvas_fingerprint()

        api_url = f"{self.base_url}/api/getGamesDownloadUrl"
        post_data = urllib.parse.urlencode({
            'id': game_id,
            'timestamp': timestamp,
            'secretKey': secret_hash,
            'canvasId': canvas_id
        }).encode('utf-8')

        request = urllib.request.Request(
            api_url,
            data=post_data,
            headers={
                'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json, text/plain, */*',
                'Origin': self.base_url,
                'Referer': download_page_url,
            })

        try:
            response = self.opener.open(request)
            response_data = response.read().decode('utf-8')

            if response_data.startswith('http'):
                return response_data

            try:
                json_data = json.loads(response_data)
                if isinstance(json_data, str) and json_data.startswith('http'):
                    return json_data
                elif isinstance(json_data, dict) and 'url' in json_data:
                    return json_data['url']
            except:
                pass

            return response_data

        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code} getting final URL")
            if e.code == 403:
                print(
                    "Error 403: Your device clock might be wrong, or request is blocked."
                )
            elif e.code == 429:
                print("Error 429: Too many requests.")
            return None
        except Exception as e:
            print(f"Error getting final URL: {e}")
            return None

    def download_file(self, url, filename):
        try:
            print(f"Downloading {filename}...")
            request = urllib.request.Request(url)
            response = self.opener.open(request)

            with open(filename, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)

            print(f"✅ Download complete: {filename}")
            return True
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False

    def _process_game(self, game):
        print(f"\nFetching details for: {game['title']}")
        
        details = self.get_game_details(game['url'])
        
        print("\n" + "="*70)
        print(f"🎮 TITLE: {details.get('title', 'N/A')}")
        print("-" * 70)
        if details.get('description'):
            print(f"📝 DESCRIPTION:")
            print(details.get('description', 'No description available.'))
            print("-" * 70)
        
        if self.show_file_size:
            print(f"💾 FILE SIZE: {details.get('file_size', 'N/A')}")
            print("-" * 70)
        
        if self.display_images:
            if details.get('image_url'):
                print(f"🖼️ COVER IMAGE URL: {details.get('image_url', 'N/A')}")
            if game.get('image_url'):
                print(f"🖼️ LIST IMAGE URL: {game.get('image_url', 'N/A')}")
            print("-" * 70)
        
        if 'game_id' in details:
            if self.automatic_download:
                print("⏳ Fetching FINAL download link...")
                final_url = self.get_final_download_url(details['game_id'])
                if final_url:
                    print(f"✅ FINAL DOWNLOAD LINK: {final_url}")
                    print("Starting download...")
                    self.download_file(final_url, f"{details.get('title', 'game')}.zip")
                else:
                    print("❌ Could not retrieve final download link.")
                    print(f"🔗 Download page: {details.get('download_page', 'N/A')}")
            else:
                print("⏳ Fetching FINAL download link...")
                final_url = self.get_final_download_url(details['game_id'])
                if final_url:
                    print(f"✅ FINAL DOWNLOAD LINK: {final_url}")
                else:
                    print("❌ Could not retrieve final download link.")
                    print(f"🔗 Download page: {details.get('download_page', 'N/A')}")
        else:
            print("❌ Could not find game ID for download.")
        print("="*70)
        
        input("\nPress Enter to continue...")

    def run(self):
        print("="*70)
        print("Koyso Game Scraper with Final Download Link")
        print("="*70)
        
        print("\nSelect genre to load games from:")
        print("-"*70)
        for key, (name, _) in self.genres.items():
            print(f"{key}. {name}")
        print("-"*70)
        
        while True:
            choice = input("\nEnter genre number (or 'quit' to exit): ").strip()
            
            if choice.lower() == 'quit':
                return
            
            if choice == '17':
                search_term = input("Enter game name to search: ").strip()
                if not search_term:
                    print("Please enter a search term.")
                    continue
                
                encoded_term = urllib.parse.quote(search_term)
                search_url = f"{self.base_url}/?keywords={encoded_term}"
                print(f"\nSearching for '{search_term}' on Koyso...")
                self.get_all_games_search(search_url, search_term)
                
                if not self.all_games:
                    print(f"No games found for '{search_term}'.")
                    continue
                break
            
            if choice in self.genres:
                print(f"\nLoading {self.genres[choice][0]} from Koyso...")
                self.get_all_games(choice)
                break
            else:
                print("Invalid selection. Please enter a valid number.")
        
        if not self.all_games:
            print("Failed to load games. Exiting.")
            return

        print(f"\nSuccessfully loaded {len(self.all_games)} games.")
        
        while True:
            print("\n" + "="*70)
            print("Loaded Games List:")
            print("-" * 70)
            for idx, game in enumerate(self.all_games, 1):
                print(f"{idx}. {game['title']}")
            print("-" * 70)
            
            action = input("\nEnter 's' to search, game number to select, 'back' for another genre, or 'quit': ").strip()
            
            if action.lower() == 'quit':
                break
            elif action.lower() == 'back':
                self.all_games = []
                self.run()
                return
            elif action.lower() == 's':
                search = input("Enter game name to search: ").strip()
                if not search:
                    print("Please enter a search term.")
                    continue
                    
                results = self.search_game(search)
                
                if not results:
                    print("No games found. Try another search term.")
                    continue
                    
                print(f"\nFound {len(results)} result(s):")
                for idx, game in enumerate(results, 1):
                    print(f"{idx}. {game['title']}")
                
                try:
                    choice = int(input(f"\nSelect game number (1-{len(results)}): "))
                    if 1 <= choice <= len(results):
                        self._process_game(results[choice-1])
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                try:
                    choice = int(action)
                    if 1 <= choice <= len(self.all_games):
                        self._process_game(self.all_games[choice-1])
                    else:
                        print(f"Invalid selection. Please enter a number between 1 and {len(self.all_games)}.")
                except ValueError:
                    print("Please enter a valid number, 's' to search, 'back', or 'quit'.")
                except Exception as e:
                    print(f"Error: {e}")
        print("="*70)
        print("Koyso Game Scraper with Final Download Link")
        print("="*70)
        
        print("\nSelect genre to load games from:")
        print("-"*70)
        for key, (name, _) in self.genres.items():
            print(f"{key}. {name}")
        print("-"*70)
        
        while True:
            choice = input("\nEnter genre number (or 'quit' to exit): ").strip()
            
            if choice.lower() == 'quit':
                return
            
            if choice in self.genres:
                print(f"\nLoading {self.genres[choice][0]} from Koyso...")
                self.get_all_games(choice)
                break
            else:
                print("Invalid selection. Please enter a valid number.")
        
        if not self.all_games:
            print("Failed to load games. Exiting.")
            return

        print(f"\nSuccessfully loaded {len(self.all_games)} games.")
        
        while True:
            print("\n" + "="*70)
            print("Loaded Games List:")
            print("-" * 70)
            for idx, game in enumerate(self.all_games, 1):
                print(f"{idx}. {game['title']}")
            print("-" * 70)
            
            action = input("\nEnter 's' to search, game number to select, 'back' for another genre, or 'quit': ").strip()
            
            if action.lower() == 'quit':
                break
            elif action.lower() == 'back':
                self.all_games = []
                self.run()
                return
            elif action.lower() == 's':
                search = input("Enter game name to search: ").strip()
                if not search:
                    print("Please enter a search term.")
                    continue
                    
                results = self.search_game(search)
                
                if not results:
                    print("No games found. Try another search term.")
                    continue
                    
                print(f"\nFound {len(results)} result(s):")
                for idx, game in enumerate(results, 1):
                    print(f"{idx}. {game['title']}")
                
                try:
                    choice = int(input(f"\nSelect game number (1-{len(results)}): "))
                    if 1 <= choice <= len(results):
                        self._process_game(results[choice-1])
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                try:
                    choice = int(action)
                    if 1 <= choice <= len(self.all_games):
                        self._process_game(self.all_games[choice-1])
                    else:
                        print(f"Invalid selection. Please enter a number between 1 and {len(self.all_games)}.")
                except ValueError:
                    print("Please enter a valid number, 's' to search, 'back', or 'quit'.")
                except Exception as e:
                    print(f"Error: {e}")

    def _process_game(self, game):
        print(f"\nFetching details for: {game['title']}")
        
        details = self.get_game_details(game['url'])
        
        print("\n" + "="*70)
        print(f"🎮 TITLE: {details.get('title', 'N/A')}")
        print("-" * 70)
        if details.get('description'):
            print(f"📝 DESCRIPTION:")
            print(details.get('description', 'No description available.'))
            print("-" * 70)
        
        if self.show_file_size:
            print(f"💾 FILE SIZE: {details.get('file_size', 'N/A')}")
            print("-" * 70)
        
        if self.display_images:
            if details.get('image_url'):
                print(f"🖼️ COVER IMAGE URL: {details.get('image_url', 'N/A')}")
            if game.get('image_url'):
                print(f"🖼️ LIST IMAGE URL: {game.get('image_url', 'N/A')}")
            print("-" * 70)
        
        if 'game_id' in details:
            if self.automatic_download:
                print("⏳ Fetching FINAL download link...")
                final_url = self.get_final_download_url(details['game_id'])
                if final_url:
                    print(f"✅ FINAL DOWNLOAD LINK: {final_url}")
                    print("Starting download...")
                    self.download_file(final_url, f"{details.get('title', 'game')}.zip")
                else:
                    print("❌ Could not retrieve final download link.")
                    print(f"🔗 Download page: {details.get('download_page', 'N/A')}")
            else:
                print("⏳ Fetching FINAL download link...")
                final_url = self.get_final_download_url(details['game_id'])
                if final_url:
                    print(f"✅ FINAL DOWNLOAD LINK: {final_url}")
                else:
                    print("❌ Could not retrieve final download link.")
                    print(f"🔗 Download page: {details.get('download_page', 'N/A')}")
        else:
            print("❌ Could not find game ID for download.")
        print("="*70)
        
        input("\nPress Enter to continue...")

def main():
    scraper = KoysoScraper()
    scraper.run()


if __name__ == "__main__":
    main()