from bls_scrapy.eztv_pipeline import EztvPipeline
from bls_scrapy.tbp_pipeline import BlsScrapyPipeline


class CommonPipeline:

    def process_item(self, item, spider):
        if spider.name == "eztv":
            return EztvPipeline().process_item(item, spider)
        
        elif spider.name == "thepirate_bay":
            return BlsScrapyPipeline().process_item(item, spider)
        else:
            return item