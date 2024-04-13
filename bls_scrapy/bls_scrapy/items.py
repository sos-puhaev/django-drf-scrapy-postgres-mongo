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