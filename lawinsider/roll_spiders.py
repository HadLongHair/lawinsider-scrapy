import os
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'lawinsider.settings')
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess


process = CrawlerProcess(get_project_settings())

process.crawl('law_dictionary')
process.crawl('law_dictionary')
process.crawl('law_dictionary')
# for spider_name in process.spider_loader.list():
#     process.crawl(spider_name)
process.start()     # the script will block here until the crawling is finished
