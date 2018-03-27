# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.exceptions import DropItem


class MongoPipeline(object):

    collection_name = 'contracts'
    # collection_name = 'dictionary'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
            # mongo_user=crawler.settings.get('MONGO_USER'),
            # mongo_pwd=crawler.settings.get('MONGO_PSW')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        # self.client.admin.authenticate(self.mongo_user, self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # if self.db[self.collection_name].find_one({'id': item['id']}):
        #     raise DropItem('Exist ! ')
        self.db[self.collection_name].insert_one(dict(item))
        return item


class lawinsiderPipeline(object):
     def process_item(self, item, spider):
        print('||||||||||||')
        print(item)
        print('||||||||||||')
        return item
