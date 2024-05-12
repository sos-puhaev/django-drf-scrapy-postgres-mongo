# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import yaml
from datetime import datetime
from .manager_scrapy import ConnectionDbScrapy
from bson import ObjectId

class BlsScrapyPipeline:

    def __init__(self):
        self.connection_db = ConnectionDbScrapy()
        with open('bls_scrapy/conf_spider/tbp.yml', 'r') as file:
            self.categories_data = yaml.safe_load(file)

    def search_cat(self, cat, sub_cat):
        for category_info in self.categories_data.get('categories', []):
            if category_info.get('cat') == cat:
                for sub_category in category_info.get('sub_cat', []):
                    if sub_category == sub_cat:
                        return category_info.get('title')

        return "Other"
    
    def date_convert(self, date):
        date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        time = date_obj.timestamp()

        return time

    def process_item(self, item, spider):

        magnet = item['magnet']
        object_id = ObjectId() # ObjectId для записей

        self.connection_db.connect_mongo()
        collection = self.connection_db.collection

        adult = False

        if item['category'] == 'Porn':
            adult = True
        else:
            adult = False
        
        object_id_str = str(object_id)
        ex_record = collection.find_one({'magnet' : magnet})
        if ex_record:
            collection.update_one({'magnet': magnet}, {
                '$set':{
                    'title':item['title'],
                    'size': self.verifield_size(item['size']),
                    'category': self.search_cat(item['category'], item['sub_category']),
                    'sub_category': item['sub_category'],
                    'url': item['url'],
                    'peers': int(item['peers']),
                    'seeds': int(item['seeds']),
                    'is_verified': item['verified'],
                    'date': item['released'],
                    'date_sort': self.date_convert(item['released']),
                    'adult': adult,
                    'source': 'thepirate_bay',
                    'magnet': item['magnet'],
                    }
                })
        else:
            collection.insert_one({
                    'id_torrent': object_id_str,
                    'title':item['title'],
                    'size': self.verifield_size(item['size']),
                    'category': self.search_cat(item['category'], item['sub_category']),
                    'sub_category': item['sub_category'],
                    'url': item['url'],
                    'peers': int(item['peers']),
                    'seeds': int(item['seeds']),
                    'is_verified': item['verified'],
                    'date': item['released'],
                    'date_sort': self.date_convert(item['released']),
                    'adult': adult,
                    'source': 'thepirate_bay',
                    'magnet': item['magnet'],
            })

            

        # all_documents = collection.find()
        # print("------------------------------")
        # for document in all_documents:
        #     print(document)
        # print("------------------------------")
        self.connection_db.client.close()

        return item

    def verifield_size(self, size):
        if size == 'null':
            size = 0
        if size == None:
            size = 0
        return size