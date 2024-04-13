# -*- coding: utf-8 -*-
import scrapy
#import cfscrape as CFRequest
from scrapy import Selector as S
from scrapy.http import Request as R
from bls_scrapy.items import BlsScrapyItem



class EztvSpider(scrapy.Spider):
    name = 'eztv'
    # custom_settings = {
    #     'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    # }
    token = None
    allowed_domains = ['eztv1.xyz']
    start_urls = ['https://eztv1.xyz/sort/100/']
    agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 YaBrowser/19.3.1.777 (beta) Yowser/2.5 Safari/537.36'

    def start_requests(self):
        requests = []
        for url in self.start_urls:
            #self.token, self.agent = CFRequest.get_tokens(url, self.agent)
            requests.append(R(url=url, cookies=self.token, headers={'User-Agent': self.agent}))
        return requests

    @staticmethod
    def _get_size(string):
        if string is None: return 0

        size = float(string[:-2])
        dim = string[-2:]

        return {
            dim == 'KB': size / 1024,
            dim == 'MB': size,
            dim == 'GB': size * 1024,
            dim == 'TB': size * 1048576
        }[True]

    @staticmethod
    def _get_released(string):
        if string is None: return 0
        import datetime
        now = datetime.datetime.now()
        if 'now' is string: return now.timestamp()

        released_array = string.split(" ")
        first = released_array[0]
        second = released_array[1] if 2 == len(released_array) else '0s'

        diff = {
            first[-1:] == 'm' and second[-1:] == 's': now - datetime.timedelta(minutes=float(first[:-1]),                                                                               seconds=float(second[:-1])),
            first[-1:] == 'h' and second[-1:] == 'm': now - datetime.timedelta(hours=float(first[:-1]),
                                                                               minutes=float(second[:-1]))
        }[True]
        return diff.timestamp()

    def parse(self, response):
        for row in response.xpath('//table[@class="forum_header_border"][4]/tr[@name="hover"]').getall():
            columns = S(text=row).xpath('//td[@class="forum_thread_post"]').getall()
            try:
                yield response.follow(
                    url=S(text=columns[1]).xpath('//a[@class="epinfo"]/@href').get(),
                    cookies=self.token,
                    headers={'User-Agent': self.agent},
                    callback=self.parse_details,
                    meta={
                        'category': 'Video',
                        'sub_category': 'Film',
                        'verified': True,
                        'url': S(text=columns[1]).xpath('//a[@class="epinfo"]/@href').get(),
                        'title': S(text=columns[1]).xpath('//a[@class="epinfo"]/text()').get(),
                        'magnet': S(text=columns[2]).xpath('//a[@class="magnet"]/@href').get(),
                        'torrent': S(text=columns[2]).xpath('//a[@class="download_1"]/@href').get(),
                        'size': self._get_size(S(text=columns[3]).xpath('.//text()').get()),
                        'released': self._get_released(S(text=columns[4]).xpath('.//text()').get())
                    }
                )
            except ValueError:
                pass

    def parse_details(self, response):
        item = BlsScrapyItem()

        info = response.xpath('//td[contains(.//text(), "Seeds: ")]').get()
        result = response.meta.copy()
        result.update({
            'seeds': S(text=info).xpath('//span[@class="stat_red"]/text()').get(),
            'peers': S(text=info).xpath('//span[@class="stat_green"]/text()').get()
        })
        item['category'] = result['category']
        item['sub_category'] = result['sub_category']
        item['verified'] = result['verified']
        item['url'] = 'https://' + self.allowed_domains[0] + result['url']
        item['title'] = result['title']
        item['magnet'] = result['magnet']
        item['size'] = result['size']
        item['released'] = result['released']
        item['seeds'] = result['seeds']
        item['peers'] = result['peers']

        # details = response.xpath('//td[contains(@style, "padding: 5px;")]').get() # TODO:
        yield item

        # yield response.follow(
        #     url=response.xpath('//td[@class="episode_left_column"]/table/tr[2]/td/a/@href').get(),
        #     cookies=self.token,
        #     headers={'User-Agent': self.agent},
        #     callback=self.parse_info,
        #     meta=result
        # )

    # def parse_info(self, response):
    #     result = response.meta.copy()
    #     # info_general = response.xpath('//td[@class="show_info_description"]').get() # TODO:
    #     info_details = response.xpath('//td[@class="show_info_banner_logo"]').get()
    #     result.update({
    #         'description': {
    #             'short': S(text=info_details).xpath('//span[@itemprop="description"][1]/p/text()').get(),
    #             'full': S(text=info_details).xpath('//span[@itemprop="description"][2]/text()').get(),
    #             'photo': response.xpath('//td[@class="show_info_main_logo"]/img/@src').get()
    #         }
    #     })
    #
    #     yield result
