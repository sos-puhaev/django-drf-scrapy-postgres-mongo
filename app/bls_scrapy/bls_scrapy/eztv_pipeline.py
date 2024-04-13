# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from pymongo import MongoClient
import datetime

class EztvPipeline:

    def date_convert(self, date):
        return datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
    
    def process_item(self, item, spider):        
        magnet = item['magnet_url']

        client = MongoClient("mongo", username="jonnijonni", password="abc234Def", authSource="mongo_db")
        db = client['mongo_db']
        collection = db['bls_scrapy']

        
        ex_record = collection.find_one({'magnet' : magnet})
        if ex_record:
            collection.update_one({'magnet': magnet}, {
                '$set':{
                    'title':item['title'],
                    'size': self.verifield_size(item['size_bytes']),
                    'category': 'Series',
                    'sub_category': 'Series',
                    'url': item['torrent_url'],
                    'peers': int(item['peers']),
                    'seeds': int(item['seeds']),
                    'is_verified': True,
                    'adult': False,
                    'date': self.date_convert(item['date_released']),
                    'date_sort': item['date_released'],
                    'source': 'eztv',
                    'magnet': item['magnet_url'],
                    'imdb_id': item['imdb_id'],
                    'season': item['season'],
                    'episode': item['episode'],
                    'quality': item['quality'],
                    'small_screen': item['small_screen'],
                    'large_screen': item['large_screen'],
                    'filename': item['filename']
                    }
                })
        else:
            collection.insert_one({
                    'title':item['title'],
                    'size': self.verifield_size(item['size_bytes']),
                    'category': 'Series',
                    'sub_category': 'Series',
                    'url': item['torrent_url'],
                    'peers': int(item['peers']),
                    'seeds': int(item['seeds']),
                    'is_verified': True,
                    'adult': False,
                    'date': self.date_convert(item['date_released']),
                    'date_sort': item['date_released'],
                    'source': 'eztv',
                    'magnet': item['magnet_url'],
                    'imdb_id': item['imdb_id'],
                    'season': item['season'],
                    'episode': item['episode'],
                    'quality': item['quality'],
                    'small_screen': item['small_screen'],
                    'large_screen': item['large_screen'],
                    'filename': item['filename']
            })

            

        # # all_documents = collection.find()
        # # print("------------------------------")
        # # for document in all_documents:
        # #     print(document)
        # # print("------------------------------")
        # client.close()

        return item
    
    def verifield_size(self, size):
        if size == 'null':
            size = 0
        return size
