# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ClauseItem(scrapy.Item):
    url = scrapy.Field()
    clause = scrapy.Field()
    clauses_text = scrapy.Field()
    sample_contracts = scrapy.Field()
    related_clauses = scrapy.Field()
    related_contracts = scrapy.Field()
    parent_clauses = scrapy.Field()
    sub_clauses = scrapy.Field()
    added_time = scrapy.Field()
    latest_update = scrapy.Field()


class DictionaryItem(scrapy.Item):
    pass