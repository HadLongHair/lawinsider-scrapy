# -*- coding: utf-8 -*-
from datetime import datetime
from scrapy_redis.spiders import RedisSpider

import scrapy
import logging
import requests
import json


LOG_FORMAT = "%(asctime)s %(message)s"
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class LawDictionaryScrapy(scrapy.Spider):
    # class LawDictionaryScrapy(RedisSpider):
    name = 'law_contracts'

    allowed_domains = ['www.lawinsider.com']
    # start_urls = ['https://www.lawinsider.com/tags/w', 'https://www.lawinsider.com/tags/x',
    #               'https://www.lawinsider.com/tags/y', 'https://www.lawinsider.com/tags/z']
    start_urls = ['https://www.lawinsider.com/tags/' + chr(97+i) for i in range(26)]
    # redis_key = 'contracts:start_urls'
    bases = 'https://www.lawinsider.com'

    def parse(self, response):
        logging.info('Spider-Dictionary running ... ')
        # follow links to detail pages
        list_urls = response.css('.dynamic-linkset.list-group-item.col-md-6::attr(href)')

        for list_url in list_urls:
            # print('poi~')
            contract_url = list_url.extract()
            request = scrapy.Request(self.bases + contract_url, callback=self.parse_list)
            yield request

        # follow pagination links
        for href in response.css('#pagination .next a::attr(href)'):
            if href:
                yield response.follow('https://www.lawinsider.com' + href.extract(), self.parse)
            else:
                # self.start_urls.append('https://www.lawinsider.com/dictionary/')
                print('1. Done!')
                pass

    def parse_list(self, response):
        item = {}
        detail_urls = response.css('.list-group-item.with-snippet')
        # list_urls = 'list-group-item with-snippet'
        for list_url in detail_urls:
            # print('poi~')
            contract_url = list_url.css('::attr(href)').extract_first()
            # print('~~~~~~~:', contract_url)
            contract_id = contract_url.split('/')[2]
            contract_info = list_url.css('blockquote p::text').extract_first()
            contract_title = list_url.css('blockquote div.title span::text').extract()
            # print('~~~~~~~:', contract_title)
            contract_date = None
            try:
                contract_date = contract_title[-1]
                contract_title = ''.join(contract_title[:-1])
            except:
                print('no date')

            item['contract_url'] = contract_url
            item['id'] = contract_id
            item['info'] = contract_info
            item['title'] = contract_title
            item['date'] = contract_date
            request = scrapy.Request(self.bases + contract_url, callback=self.parse_detail)
            request.meta['item'] = item
            yield request

        # follow pagination links
        for href in response.css('#pagination .next a::attr(href)'):
            if href:
                yield response.follow('https://www.lawinsider.com' + href.extract(), self.parse_list)
            else:
                # self.start_urls.append('https://www.lawinsider.com/dictionary/')
                print('1. Done!')
                pass

    def parse_detail(self, response):
        item = response.meta['item']
        cc = None
        # TODO
        ct = 'Acquisition Agreement'.lower()
        try:
            # cc = item['contract_url'].split('/')[3]
            cc = 'acknowledgement-and-agreement'
        except:
            pass

        # contract_content
        contract_content = response.css('.row.contract-content')
        item['contract_content_html'] = contract_content.extract_first()
        item['contract_content'] = ''.join(contract_content.css('.row.contract-content *::text').extract())

        # sidebar-similar-contracts
        item['similar_contracts'] = []
        # if ct:
        # similar_contracts = self.get_query(
        #         'https://www.lawinsider.com/search/api?type=tag&size=10&q={0}'.format(ct))
        #     item['similar_contracts'] = similar_contracts['results']['tag']

        # sidebar-related-clauses-by-tag
        # https://www.lawinsider.com/search/api/aggs?type=clause&size=10&filter=tag:
        item['most_common_clauses'] = []
        # if cc:
        #     most_common_clauses = self.get_query(
        #         'https://www.lawinsider.com/search/api/aggs?type=clause&size=10&filter=tag:{0}'.format(cc))
        #     # print('=====-=-=-=-=-=-=-')
        #     # print(most_common_clauses)
        #     item['most_common_clauses'] = most_common_clauses

        # items found
        item['items_found'] = []
        items_found = response.css('#sidebar-related-entities-list li a:nth-child(2)')
        for f in items_found:
            item['items_found'].append(
                {'url': f.css('::attr(href)').extract_first(), 'title': f.css('::text').extract_first()})
        # tags
        item['label'] = []
        tags = response.css('.tags li a')
        for t in tags:
            tag = t.css('i::attr(class)').extract()
            try:
                tag = tag[0].split('icon icon-')[1]
            except:
                tag = 'no_tag'
            # item['tags'] = tag
            item['label'].append(
                {tag: ''.join(t.css('::text').extract() or []).replace('\n', '').strip(),
                 'url': t.css('::attr(href)').extract_first()})
            pass

        item['added_on'] = datetime.utcnow()
        item['last_updated'] = datetime.utcnow()
        yield item

        next_href = response.css('#pagination .next a::attr(href)')
        for n in next_href:
            if n:
                yield response.follow('https://www.lawinsider.com' + n.extract(), self.parse_detail)
            else:
                print('Next Clause Ref...')
                pass

    def get_query(self, url):
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en',
            'Origin': 'https://www.lawinsider.com',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        try:
            r = requests.get(url, headers=headers)
            return json.loads(r.text)
        except:
            return None