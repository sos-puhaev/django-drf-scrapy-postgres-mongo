# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request as R
import json
from bls_scrapy.items import BlsScrapyItemYts
import psycopg2
import urllib.parse

class YtsTorrentSpider(scrapy.Spider):
    name = 'yts_torrent'
    allowed_domains = ['yts.torrentz3.org'] #edit
    limit = 1 #edit
    offset = 1 #edit
    start_urls = ['https://yts.torrentz3.org/'] #edit

    trackers = ["udp://glotorrents.pw:6969/announce", "udp://tracker.opentrackr.org:1337/announce",
                "udp://torrent.gresille.org:80/announce", "udp://tracker.openbittorrent.com:80", 
                "udp://tracker.coppersurfer.tk:6969", "udp://tracker.leechers-paradise.org:6969", 
                "udp://p4p.arenabg.ch:1337", "udp://tracker.internetwarriors.net:1337"]
    agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 YaBrowser/19.3.1.777 (beta) Yowser/2.5 Safari/537.36'
    count = 1

    def __init__(self, *args, **kwargs):
        super(YtsTorrentSpider, self).__init__(*args, **kwargs)
        self.limit = int(self.settings_spider()['limit'])
        self.offset = int(self.settings_spider()['offset'])

        allowed_url = self.settings_spider()['allowed_domain']
        self.allowed_domains = [value.strip() for value in allowed_url.split(',')]

        url_parse = self.settings_spider()['urlParse']
        self.start_urls = [value.strip() for value in url_parse.split(',')]
    
    def settings_spider(self):
        try:
            connection = psycopg2.connect(
                host="postgres",
                database="postgres",
                user="app_db_user",
                password="supersecretpassword"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT \"limit\", \"offset\", allowed_domains, url_parse FROM settings_yts;")
            existing_data = cursor.fetchone()

            cursor.close()
            connection.close()

            if existing_data:
                limit, offset, allowed_domain, urlParse = existing_data
                return {"limit": limit, "offset": offset, "allowed_domain": allowed_domain, "urlParse": urlParse}
            else:
                return {"limit": None, "offset": None, "allowed_domain": None, "urlParse": None}

        except Exception as e:
            print(f"Error: {e}")
            return {"limit": None, "offset": None, "allowed_domain": None, "urlParse": None}

    def start_requests(self):
        url = ''.join([self.start_urls[0] ,f'api/v2/list_movies.json?page=1&limit={self.offset}']).format(self.offset)
        yield R(url, callback=self.parse)

    def parse(self, response):
        json_res = response.body
        if json_res:
            try:
                json_response = json.loads(json_res)
                data = json_response.get('data', [])
                torrents_index = data.get('movies', [])

                for torrent in torrents_index:
                    imdb_id = torrent.get('imdb_code'),
                    title = torrent.get('title_long'),
                    for nested_torrent in torrent.get('torrents'):
                        item = BlsScrapyItemYts(
                            imdb_id = imdb_id[0],
                            title = ' '.join([str(title[0]), str(nested_torrent.get('quality'))]),
                            torrent_url = nested_torrent.get('url'),
                            seeds = nested_torrent.get('seeds'),
                            peers = nested_torrent.get('peers'),
                            size_bytes = nested_torrent.get('size_bytes'),
                            quality = nested_torrent.get('quality'),
                            date_released = nested_torrent.get('date_uploaded_unix'),
                            date_released_view = nested_torrent.get('date_uploaded'),
                            magnet_url = self.magnet_generate(nested_torrent.get('hash'), title)
                        )
                        yield item

                if self.count != self.limit:
                    self.count += 1
                    next_url = ''.join([self.start_urls[0], f'api/v2/list_movies.json?page={self.count}&limit={self.offset}'])
                    yield R(next_url, callback=self.parse)

            except json.decoder.JSONDecodeError as e:
                print(f"Ошибка разбора JSON: {e}")
        else:
            if self.count != self.limit:
                self.count += 1
                next_url = ''.join([self.start_urls[0], f'api/v2/list_movies.json?page={self.count}&limit={self.offset}'])
                yield R(next_url, callback=self.parse)


    def magnet_generate(self, hash, movie_name):
        params = {
            "xt": f"urn:btih:{hash}",
            "dn": movie_name,
            "tr": self.trackers
        }
        magnet_link = "magnet:?" + urllib.parse.urlencode(params)
        decoded_magnet_link = urllib.parse.unquote(magnet_link)
        return str(decoded_magnet_link)
        