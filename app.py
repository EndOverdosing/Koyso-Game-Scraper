from flask import Flask, render_template, request, jsonify, Response
import urllib.request
import urllib.parse
import re
import json
import html
import hashlib
import time
import urllib.error
from functools import wraps

app = Flask(__name__)

class KoysoScraper:
    def __init__(self):
        self.base_url = "https://koyso.to"
        self.all_games = []
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
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
            '16': ('LAN connection', '/category/lan')
        }
        self.secret_key = "f6i6@m29r3fwi^yqd"
        self.request_delay = 0.05

    def fetch_page(self, url):
        try:
            time.sleep(self.request_delay)
            request = urllib.request.Request(url)
            response = self.opener.open(request)
            content = response.read()
            return content.decode('utf-8')
        except urllib.error.HTTPError as e:
            return ""
        except Exception as e:
            return ""

    def _extract_games_from_page(self, html_content):
        games = []
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
        return games

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

    def get_games(self, genre_id=None, search_query=None, page=1):
        games = []
        
        if search_query:
            encoded_query = urllib.parse.quote(search_query)
            if page == 1:
                url = f"{self.base_url}/?keywords={encoded_query}"
            else:
                url = f"{self.base_url}/?keywords={encoded_query}&page={page}"
        elif genre_id and genre_id in self.genres:
            genre_name, genre_url = self.genres[genre_id]
            if page == 1:
                url = f"{self.base_url}{genre_url}"
            else:
                url = f"{self.base_url}{genre_url}?page={page}"
        else:
            if page == 1:
                url = f"{self.base_url}/"
            else:
                url = f"{self.base_url}/?page={page}"

        html_content = self.fetch_page(url)
        if html_content:
            games = self._extract_games_from_page(html_content)
            has_next = self._has_next_page(html_content, page)
        else:
            has_next = False
            
        return games, has_next

    def get_game_details(self, game_url):
        html_content = self.fetch_page(game_url)
        if not html_content:
            return None

        details = {}

        title_match = re.search(r'<h1 class="content_title"[^>]*>(.*?)</h1>', html_content, re.DOTALL)
        if title_match:
            details['title'] = html.unescape(re.sub(r'<[^>]*>', '', title_match.group(1)).strip())

        description_match = re.search(r'<div class="content_body">.*?<p>(.*?)</p>', html_content, re.DOTALL)
        if description_match:
            details['description'] = html.unescape(re.sub(r'<[^>]*>', '', description_match.group(1)).strip())

        image_match = re.search(r'<div class="capsule_div">.*?<img[^>]*src="([^"]*)"', html_content, re.DOTALL)
        if image_match:
            details['image_url'] = image_match.group(1)

        size_match = re.search(r'<span>Size</span>\s*<span>([^<]+)</span>', html_content)
        if size_match:
            details['file_size'] = size_match.group(1).strip()

        download_match = re.search(r'onclick="download\(\)".*?href="/download/(\d+)"', html_content, re.DOTALL)
        if download_match:
            details['game_id'] = download_match.group(1)
            details['download_page'] = f"{self.base_url}/download/{download_match.group(1)}"
        else:
            download_match = re.search(r'<button[^>]*onclick="[^"]*/download/(\d+)[^"]*"', html_content)
            if download_match:
                details['game_id'] = download_match.group(1)
                details['download_page'] = f"{self.base_url}/download/{download_match.group(1)}"

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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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
            if e.code == 429:
                return "rate_limited"
            return None
        except Exception as e:
            return None

scraper = KoysoScraper()

def rate_limit_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rate_limited' in request.cookies:
            return jsonify({'error': 'Rate limited. Try again later.'}), 429
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/games')
@rate_limit_check
def get_games():
    genre_id = request.args.get('genre', '1')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    
    games, has_next = scraper.get_games(genre_id, search, page)
    return jsonify({
        'games': games,
        'has_next': has_next,
        'page': page
    })

@app.route('/api/game/<game_id>')
@rate_limit_check
def get_game(game_id):
    game_url = f"https://koyso.to/game/{game_id}"
    details = scraper.get_game_details(game_url)
    if details:
        return jsonify(details)
    return jsonify({'error': 'Game not found'}), 404

@app.route('/api/download/<game_id>')
@rate_limit_check
def get_download_url(game_id):
    final_url = scraper.get_final_download_url(game_id)
    if final_url == "rate_limited":
        response = jsonify({'error': 'rate_limited'})
        response.set_cookie('rate_limited', 'true', max_age=60)
        return response, 429
    elif final_url:
        return jsonify({'url': final_url})
    return jsonify({'error': 'Failed to get download URL'}), 500

if __name__ == '__main__':
    app.run(debug=True)