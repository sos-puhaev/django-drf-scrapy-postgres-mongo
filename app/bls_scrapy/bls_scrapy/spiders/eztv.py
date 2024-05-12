# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request as R
import json
from bls_scrapy.items import BlsScrapyItemEztv
from ..manager_scrapy import ConnectionDbScrapy

class EztvSpider(scrapy.Spider):
    name = 'eztv'
    allowed_domains = ['eztvx.to']
    limit = 1
    offset = 1
    start_urls = ['https://eztvx.to']
    agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 YaBrowser/19.3.1.777 (beta) Yowser/2.5 Safari/537.36'
    count = 1

    def __init__(self, *args, **kwargs):
        super(EztvSpider, self).__init__(*args, **kwargs)
        self.connection_db = ConnectionDbScrapy()
        self.limit = int(self.settings_spider()['limit'])
        self.offset = int(self.settings_spider()['offset'])

        allowed_url = self.settings_spider()['allowed_domain']
        self.allowed_domains = [value.strip() for value in allowed_url.split(',')]

        url_parse = self.settings_spider()['urlParse']
        self.start_urls = [value.strip() for value in url_parse.split(',')]
    
    def settings_spider(self):
        try:
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor
            cursor.execute("SELECT \"limit\", \"offset\", allowed_domains, url_parse FROM settings_eztv;")
            existing_data = cursor.fetchone()

            cursor.close()
            self.connection_db.connection.close()

            if existing_data:
                limit, offset, allowed_domain, urlParse = existing_data
                return {"limit": limit, "offset": offset, "allowed_domain": allowed_domain, "urlParse": urlParse}
            else:
                return {"limit": None, "offset": None, "allowed_domain": None, "urlParse": None}

        except Exception as e:
            print(f"Error: {e}")
            return {"limit": None, "offset": None, "allowed_domain": None, "urlParse": None}

    def start_requests(self):
        url = ''.join([self.start_urls[0] ,f'/api/get-torrents?limit={self.limit}&page=1']).format(self.limit)
        yield R(url, callback=self.parse)

    def parse(self, response):
        if self.offset > 100:
            self.offset = 100
        elif self.offset < 0:
            self.offset = 1

        if self.limit > 100:
            self.limit = 100
        elif self.limit < 0:
            self.limit = 1
        
        json_response = json.loads(response.body)
        torrents = json_response.get('torrents', [])
        for torrent in torrents:
            item = BlsScrapyItemEztv(
                imdb_id = torrent.get('imdb_id'),
                filename = torrent.get('filename'),
                torrent_url = torrent.get('torrent_url'),
                magnet_url = torrent.get('magnet_url'),
                title = torrent.get('title'),
                seeds = torrent.get('seeds'),
                peers = torrent.get('peers'),
                season = torrent.get('season'),
                episode = torrent.get('episode'),
                quality = self.search_for_quality(torrent.get('title')),
                small_screen = torrent.get('small_screenshot'),
                large_screen = torrent.get('large_screenshot'),
                date_released = torrent.get('date_released_unix'),
                size_bytes = torrent.get('size_bytes')
            )
            yield item

        if self.count != self.offset:
            self.count += 1
            next_url = ''.join([self.start_urls[0], f'/api/get-torrents?limit={self.limit}&page={self.count}'])
            yield R(next_url, callback=self.parse)

    def search_for_quality(self, offer):
        if "720p" in offer:
            return '720p'
        elif "1080p" in offer:
            return '1080p'
        elif "480p" in offer:
            return '480p'
        return 'Other'