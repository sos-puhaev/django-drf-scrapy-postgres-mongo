import scrapy
from scrapy import Selector as S
from scrapy.http import Request as R
import re
from bls_scrapy.items import BlsScrapyItem
from ..manager_scrapy import ConnectionDbScrapy

class ThepirateBaySpider(scrapy.Spider):
    name = "thepirate_bay"
    start_page = 1
    max_page = 1
    allowed_domains = []
    start_urls = []
    agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 YaBrowser/19.3.1.777 (beta) Yowser/2.5 Safari/537.36'

    def __init__(self, *args, **kwargs):
        super(ThepirateBaySpider, self).__init__(*args, **kwargs)
        self.connection_db = ConnectionDbScrapy()
        self.start_page = self.settings_spider()['start_page']
        self.max_page = self.settings_spider()['end_page']

        url_parse = self.settings_spider()['url_parse']
        self.allowed_domains = [value.strip() for value in url_parse.split(',')]

        url_start = self.settings_spider()['start_url']
        self.start_urls = [value.strip() for value in url_start.split(',')]

    def start_requests(self):
        requests = []
        for url in self.start_urls:
            requests.append(R(url=url, headers={'User-Agent': self.agent}))
        return requests

    def parse_top(self, response):
        for row in response.css('div.detName a.detLink::attr(href)').getall():
            yield scrapy.Request(url=row, callback=self.parse_torrent, meta={'torrent_url': row})

    def settings_spider(self):
        try:
            self.connection_db.connect_pg()
            cursor = self.connection_db.cursor
            cursor.execute("SELECT start_page, end_page, url_parse, start_url FROM settings_tpb;")
            existing_data = cursor.fetchone()

            cursor.close()
            self.connection_db.connection.close()

            if existing_data:
                start_page, end_page, url_parse, start_url = existing_data
                return {"start_page": start_page, "end_page": end_page, "url_parse": url_parse, "start_url": start_url}
            else:
                return {"start_page": None, "end_page": None, "url_parse": None, "start_url": None}

        except Exception as e:
            print(f"Error: {e}")
            return {"start_page": None, "end_page": None, "url_parse": None, "start_url": None}
        
    def parse(self, response):
        for row in response.xpath("//table/tr/td[@class='categoriesContainer']/dl/dt").getall():
            category_url = response.urljoin(S(text=row).xpath('//a/@href').get())
            if category_url is not None:
                self.start_page = 1
                if category_url == 'https://tpb.party/top/100':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_top
                    )
                elif category_url == 'https://tpb.party/top/200':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_top
                    )
                elif category_url == 'https://tpb.party/top/300':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_top
                    )
                elif category_url == 'https://tpb.party/top/400':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_top
                    )
                elif category_url == 'https://tpb.party/top/500':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_top
                    )
                elif category_url == 'https://tpb.party/top/600':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_top
                    )
                elif category_url == 'https://tpb.party/browse/100':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_category_100
                    )
                elif category_url == 'https://tpb.party/browse/200':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_category_200
                    )
                elif category_url == 'https://tpb.party/browse/300':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_category_300
                    )
                elif category_url == 'https://tpb.party/browse/400':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_category_400
                    )
                elif category_url == 'https://tpb.party/browse/500':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_category_500
                    )
                elif category_url == 'https://tpb.party/browse/600':
                    yield response.follow(
                        url=category_url,
                        headers={'User-Agent': self.agent},
                        callback=self.parse_category_600
                    )
                    

    def parse_category_100(self, response):
        base_url = ('https://tpb.party/browse/100/{page}/3')
        for row in response.css('div.detName a.detLink::attr(href)').getall():
            yield scrapy.Request(url=row, callback=self.parse_torrent, meta={'torrent_url': row})
        
        self.start_page += 1
        if self.start_page <= self.max_page:
            next_page = base_url.format(page=self.start_page)
            yield scrapy.Request(url=next_page, callback=self.parse_category_100)

    def parse_category_200(self, response):
        base_url = ('https://tpb.party/browse/200/{page}/3')
        for row in response.css('div.detName a.detLink::attr(href)').getall():
            yield scrapy.Request(url=row, callback=self.parse_torrent, meta={'torrent_url': row})
        
        self.start_page += 1
        if self.start_page <= self.max_page:
            next_page = base_url.format(page=self.start_page)
            yield scrapy.Request(url=next_page, callback=self.parse_category_200)
    
    def parse_category_300(self, response):
        base_url = ('https://tpb.party/browse/300/{page}/3')
        for row in response.css('div.detName a.detLink::attr(href)').getall():
            yield scrapy.Request(url=row, callback=self.parse_torrent, meta={'torrent_url': row})
        
        self.start_page += 1
        if self.start_page <= self.max_page:
            next_page = base_url.format(page=self.start_page)
            yield scrapy.Request(url=next_page, callback=self.parse_category_300)

    def parse_category_400(self, response):
        base_url = ('https://tpb.party/browse/400/{page}/3')
        for row in response.css('div.detName a.detLink::attr(href)').getall():
            yield scrapy.Request(url=row, callback=self.parse_torrent, meta={'torrent_url': row})
        
        self.start_page += 1
        if self.start_page <= self.max_page:
            next_page = base_url.format(page=self.start_page)
            yield scrapy.Request(url=next_page, callback=self.parse_category_400)
    
    def parse_category_500(self, response):
        base_url = ('https://tpb.party/browse/500/{page}/3')
        for row in response.css('div.detName a.detLink::attr(href)').getall():
            yield scrapy.Request(url=row, callback=self.parse_torrent, meta={'torrent_url': row})
        
        self.start_page += 1
        if self.start_page <= self.max_page:
            next_page = base_url.format(page=self.start_page)
            yield scrapy.Request(url=next_page, callback=self.parse_category_500)

    def parse_category_600(self, response):
        base_url = ('https://tpb.party/browse/600/{page}/3')
        for row in response.css('div.detName a.detLink::attr(href)').getall():
            yield scrapy.Request(url=row, callback=self.parse_torrent, meta={'torrent_url': row})
        
        self.start_page += 1
        if self.start_page <= self.max_page:
            next_page = base_url.format(page=self.start_page)
            yield scrapy.Request(url=next_page, callback=self.parse_category_600)
            
    def parse_torrent(self, response):
        item = BlsScrapyItem()
        title = response.css('#title::text').get()
        data = response.css('dl.col2 dt:contains("Uploaded:") + dd::text').extract_first()
        up_date = data.replace("GMT", "").strip()
        torrent_url = response.meta.get('torrent_url')
        category_text = response.css('dl.col1 dt:contains("Type:") + dd a::text').get().split(" > ")
        if len(category_text) == 2:
            category, sub_category = category_text

        size_text = size_converter(response.css('dl.col1 dt:contains("Size:") + dd::text').get())
        

        the_verefied = response.css('dl.col2 dt:contains("By:") + dd i::text').get()
        if the_verefied == 'Anonymous':
            is_verified = False
        else: is_verified = True

        seeds = response.css('dl.col2 dt:contains("Seeders:") + dd::text').get()
        peers = response.css('dl.col2 dt:contains("Leechers:") + dd::text').get()
        magnet_link = response.css('div.download a[title="Get this torrent"]::attr(href)').get()

        item['category'] = category
        item['verified'] = is_verified
        item['sub_category'] = sub_category
        item['url'] = torrent_url
        item['title'] = title
        item['magnet'] = magnet_link
        item['seeds'] = seeds
        item['peers'] = peers
        item['size'] = size_text
        item['released'] = up_date

        yield item
        
            
def size_converter(size_text):
    if size_text:
        size_text = size_text.replace('\xa0', '').replace(',', '.')
        numeric_part = re.search(r'(\d+\.\d+)', size_text)
        if numeric_part:
            size_in_megabytes = float(numeric_part.group(1))
            size = round(size_in_megabytes * 1024)
            return size
    return None
       