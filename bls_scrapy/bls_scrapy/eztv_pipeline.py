# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from pymongo import MongoClient

class EztvPipeline:

    def process_item(self, item, spider):

        magnet = item['magnet']

        client = MongoClient("mongo", username="jonnijonni", password="abc234Def", authSource="mongo_db")
        db = client['mongo_db']
        collection = db['bls_scrapy']
        adult = False

        if item['category'] == 'Porn':
            adult = True
        else:
            adult = False

        
        ex_record = collection.find_one({'magnet' : magnet})
        if ex_record:
            collection.update_one({'magnet': magnet}, {
                '$set':{
                    'title':item['title'],
                    'size': item['size'],
                    'category': item['category'],
                    'sub_category': item['sub_category'],
                    'url': item['url'],
                    'peers': int(item['peers']),
                    'seeds': int(item['seeds']),
                    'is_verified': item['verified'],
                    'date': item['released'],
                    'adult': adult,
                    'source': 'eztv',
                    'magnet': item['magnet'],
                    }
                })
        else:
            collection.insert_one({
                    'title':item['title'],
                    'size': item['size'],
                    'category': item['category'],
                    'sub_category': item['sub_category'],
                    'url': item['url'],
                    'peers': int(item['peers']),
                    'seeds': int(item['seeds']),
                    'is_verified': item['verified'],
                    'date': item['released'],
                    'adult': adult,
                    'source': 'eztv',
                    'magnet': item['magnet'],
            })

            

        # all_documents = collection.find()
        # print("------------------------------")
        # for document in all_documents:
        #     print(document)
        # print("------------------------------")
        client.close()

        return item
