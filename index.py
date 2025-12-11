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
            return ""
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def get_all_games(self):
        search_url = f"{self.base_url}/?keywords=GTA"
        print(f"Fetching GTA games from search...")
        html_content = self.fetch_page(search_url)
        
        if html_content:
            self._extract_games_from_page(html_content)
        
        page = 1
        while True:
            url = f"{self.base_url}/?page={page}"
            print(f"Fetching page {page}...")
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
                print(
                    "Error 429: Download rate limited (one every 5 minutes). Please wait."
                )
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

    def run(self):
        print("="*70)
        print("Koyso Game Scraper with Final Download Link")
        print("="*70)
        
        print("\nLoading games from Koyso...")
        self.get_all_games()

        if not self.all_games:
            print("Failed to load games. Exiting.")
            return

        print(f"\nSuccessfully loaded {len(self.all_games)} games.")

        while True:
            print("\n" + "="*70)
            search = input("Enter game name to search (or 'quit' to exit): ").strip()

            if search.lower() == 'quit':
                break

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
                    selected = results[choice-1]
                    print(f"\nFetching details for: {selected['title']}")

                    details = self.get_game_details(selected['url'])

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
                        if selected.get('image_url'):
                            print(f"🖼️ LIST IMAGE URL: {selected.get('image_url', 'N/A')}")
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
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
            except Exception as e:
                print(f"Error: {e}")

def main():
    scraper = KoysoScraper()
    scraper.run()


if __name__ == "__main__":
    main()