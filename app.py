from flask import Flask, render_template, jsonify, request
import urllib.request
import urllib.parse
import re
import json
import html
import hashlib
import time
import urllib.error

app = Flask(__name__)

class KoysoScraper:
    def __init__(self):
        self.base_url = "https://koyso.to"
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
        ]
        self.genres = {
            '1': ('All', '/'),
            '2': ('Action', '/category/action'),
            '3': ('Adventure', '/category/adventure'),
            '4': ('R18+', '/category/r18'),
            '5': ('Shooting', '/category/shooting'),
            '6': ('Casual', '/category/casual'),
            '7': ('Sports', '/category/sports_racing'),
            '8': ('Simulation', '/category/simulation'),
            '9': ('RPG', '/category/rpg'),
            '10': ('Strategy', '/category/strategy'),
            '11': ('Fighting', '/category/fighting'),
            '12': ('Horror', '/category/horror'),
            '13': ('RTS', '/category/rts'),
            '14': ('Card', '/category/card'),
            '15': ('Indie', '/category/indie'),
            '16': ('LAN', '/category/lan')
        }
        self.secret_key = "f6i6@m29r3fwi^yqd"

    def fetch_page(self, url):
        try:
            time.sleep(0.05)
            request = urllib.request.Request(url)
            response = self.opener.open(request)
            content = response.read()
            return content.decode('utf-8')
        except:
            return ""

    def get_games_by_genre(self, genre_id, page=1):
        games = []
        if genre_id in self.genres:
            genre_name, genre_url = self.genres[genre_id]
            base_url = f"{self.base_url}{genre_url}"
            url = f"{base_url}?page={page}" if page > 1 else base_url
            
            html_content = self.fetch_page(url)
            if not html_content:
                return games, False
                
            game_item_pattern = r'<a class="game_item"[^>]*href="([^"]*)"[^>]*>.*?<img[^>]*(?:data-src|src)="([^"]*)"[^>]*>.*?<span[^>]*>([^<]*)</span>'
            game_item_matches = re.findall(game_item_pattern, html_content, re.DOTALL)
            
            for game_url, image_url, game_title in game_item_matches:
                game = {
                    'title': html.unescape(game_title.strip()),
                    'url': urllib.parse.urljoin(self.base_url, game_url.strip()),
                    'id': game_url.strip().split('/')[-1],
                    'image_url': image_url
                }
                games.append(game)
            
            has_next = self._has_next_page(html_content, page)
        
        return games, has_next

    def _has_next_page(self, html_content, current_page):
        next_page_pattern = r'<a[^>]*href="[^"]*\?page={}"[^>]*>'.format(current_page + 1)
        if re.search(next_page_pattern, html_content, re.IGNORECASE):
            return True
        return False

    def get_game_details(self, game_url):
        html_content = self.fetch_page(game_url)
        if not html_content:
            return {'error': 'Failed to fetch page'}

        details = {}

        title_match = re.search(r'<h1 class="content_title"[^>]*>(.*?)</h1>', html_content, re.DOTALL)
        if title_match:
            details['title'] = html.unescape(re.sub(r'<[^>]*>', '', title_match.group(1)).strip())

        description_match = re.search(r'<div class="content_body">(.*?)</div>', html_content, re.DOTALL)
        if description_match:
            description_text = description_match.group(1)
            description_text = re.sub(r'<[^>]*>', '', description_text)
            description_text = re.sub(r'\s+', ' ', description_text).strip()
            details['description'] = html.unescape(description_text)

        image_match = re.search(r'<div class="capsule_div">.*?<img[^>]*src="([^"]*)"', html_content, re.DOTALL)
        if image_match:
            details['image_url'] = image_match.group(1)

        video_match = re.search(r'<video[^>]*src="([^"]*)"', html_content)
        if video_match:
            details['video_url'] = video_match.group(1)

        size_match = re.search(r'<span>Size</span>\s*<span>([^<]+)</span>', html_content)
        if size_match:
            details['file_size'] = size_match.group(1).strip()

        download_match = re.search(r'onclick="download\(\)".*?href="/download/(\d+)"', html_content, re.DOTALL)
        if download_match:
            details['game_id'] = download_match.group(1)
        else:
            download_match = re.search(r'<button[^>]*onclick="[^"]*/download/(\d+)[^"]*"', html_content)
            if download_match:
                details['game_id'] = download_match.group(1)

        return details

    def generate_hash(self, timestamp, game_id):
        data = timestamp + game_id + self.secret_key
        return hashlib.sha256(data.encode()).hexdigest()

    def get_final_download_url(self, game_id):
        download_page_url = f"{self.base_url}/download/{game_id}"
        html_content = self.fetch_page(download_page_url)
        if not html_content:
            return None

        timestamp = str(int(time.time()))
        secret_hash = self.generate_hash(timestamp, game_id)

        api_url = f"{self.base_url}/api/getGamesDownloadUrl"
        post_data = urllib.parse.urlencode({
            'id': game_id,
            'timestamp': timestamp,
            'secretKey': secret_hash,
            'canvasId': 123456789
        }).encode('utf-8')

        request = urllib.request.Request(
            api_url,
            data=post_data,
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/x-www-form-urlencoded',
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
        except:
            return None

scraper = KoysoScraper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/genres')
def get_genres():
    genres_list = []
    for key, (name, _) in scraper.genres.items():
        genres_list.append({'id': key, 'name': name})
    return jsonify(genres_list)

@app.route('/games/<genre_id>/<int:page>')
def get_games(genre_id, page):
    games, has_next = scraper.get_games_by_genre(genre_id, page)
    return jsonify({'games': games, 'has_next': has_next})

@app.route('/details')
def get_details():
    game_url = request.args.get('url')
    if not game_url:
        return jsonify({'error': 'No URL provided'})
    
    details = scraper.get_game_details(game_url)
    
    if 'game_id' in details:
        download_url = scraper.get_final_download_url(details['game_id'])
        details['final_download_url'] = download_url
    
    return jsonify(details)

if __name__ == '__main__':
    app.run(debug=True)