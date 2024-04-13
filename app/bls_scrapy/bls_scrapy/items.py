# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class BlsScrapyItem(scrapy.Item):
    category = scrapy.Field()
    verified = scrapy.Field()
    sub_category = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    magnet = scrapy.Field()
    seeds = scrapy.Field()
    peers = scrapy.Field()
    size = scrapy.Field()
    released = scrapy.Field()
    
class BlsScrapyItemEztv(scrapy.Item):
    imdb_id = scrapy.Field()
    filename = scrapy.Field()
    torrent_url = scrapy.Field()
    magnet_url = scrapy.Field()
    title = scrapy.Field()
    seeds = scrapy.Field()
    peers = scrapy.Field()
    season = scrapy.Field()
    episode = scrapy.Field()
    quality = scrapy.Field()
    small_screen = scrapy.Field()
    large_screen = scrapy.Field()
    date_released = scrapy.Field()
    size_bytes = scrapy.Field()

class BlsScrapyItemYts(scrapy.Item):
    imdb_id = scrapy.Field()
    title = scrapy.Field()
    torrent_url = scrapy.Field()
    seeds = scrapy.Field()
    peers = scrapy.Field()
    quality = scrapy.Field()
    size_bytes = scrapy.Field()
    date_released = scrapy.Field()
    date_released_view = scrapy.Field()
    magnet_url = scrapy.Field()