# -*- coding: utf-8 -*-
# from bs4 import BeautifulSoup as BS
from lawinsider.items import ClauseItem
from datetime import datetime
from scrapy_redis.spiders import RedisSpider

import scrapy
import logging

LOG_FORMAT = "%(asctime)s %(message)s"
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)


# class LawDictionaryScrapy(RedisSpider):
class LawDictionaryScrapy(scrapy.Spider):
    name = 'law_dictionary'

    allowed_domains = ['www.lawinsider.com']
    start_urls = ['https://www.lawinsider.com/dictionary/a']
    # redis_key = 'dictionary:start_urls'
    bases = 'https://www.lawinsider.com'

    def parse(self, response):
        logging.info('Spider-Dictionary running ... ')
        # follow links to detail pages
        detail_list = response.css('.list-group-item.clause-snippet')

        raw_dictionary = response.css('.list-group-item.clause-snippet')
        # assert 1 == 2
        for i, list_url in enumerate(detail_list):
            # print('poi~')
            item = {}
            # item['referer'] = response.request.headers.get('Referer', None).decode('utf-8')
            item['url'] = list_url.css('a::attr(href)').extract_first()
            try:
                item['dictionary'] = raw_dictionary[i].css('div.snippet-title span::text').extract()[0].replace('\n',
                                                                                                                '')
            except:
                item['dictionary'] = None
                logging.error('~Fail~')

            request = scrapy.Request(self.bases + item['url'], callback=self.parse_detail)
            request.meta['item'] = item
            yield request

        # follow pagination links
        for href in response.css('#pagination .next a::attr(href)'):
            if href:
                yield response.follow('https://www.lawinsider.com' + href.extract(), self.parse)
            else:
                # self.start_urls.append('https://www.lawinsider.com/dictionary/')
                print('1. Done!')
                pass

    def parse_detail(self, response):
        item = response.meta['item']
        paper1 = None
        paper2 = None
        paper3 = None

        papers = response.css('.col-lg-9.col-md-9.col-sm-12.col-xs-12 .paper')
        for paper in papers:
            print('00000000=========00000')
            if 'Definition of' in ''.join(paper.css('h1::text').extract()):
                paper1 = paper
                print('1')
                # Definition
                item['definition'] = []
                definition_list = []
                definitions = paper1.css('ol li.snippet-content')
                for definition in definitions:
                    try:
                        definition_text = ''.join(definition.css('*::text').extract()).replace('\n', '').strip()
                        print('==========')
                        print(definition_text)
                        if definition_text:
                            definition_list.append(definition_text)
                    except Exception as e:
                        logging.error("No text")

                item['definition'] = definition_list

            if 'Examples of' in ''.join(paper.css('h3::text').extract()):
                paper2 = paper
                print('2')

                # examples
                item['example'] = []
                example_list = []
                examples = paper2.css('ol li')
                for example in examples:
                    try:
                        example_text = ''.join(example.css('*::text').extract()).replace('\n', '').strip()
                        example_list.append(example_text)
                    except Exception as e:
                        logging.error("No example text")

                item['example'] = example_list

            if 'Definition of' in ''.join(paper.css('h3::text').extract()):
                paper3 = paper
                print('3')

                # Contract Tags TODO
                item['contract_tags'] = []
                contract_tags = paper3.css('h3')
                for i, ct in enumerate(contract_tags):
                    contract_tag = {}
                    contract_tag['name'] = ct.css('a::text').extract_first()
                    contract_tag['url'] = ct.css('a::attr(href)').extract_first()
                    print('==========')
                    print('~~~~~~~~~~')
                    contract_tag['text'] = ''.join(paper3.css('p')[i].css('*::text').extract()).replace('\n', '').strip()
                    item['contract_tags'].append(contract_tag)

        # Related Definitions
        related_definitions = response.css('.paper-sidebar .list-group .list-group-item a')
        item['related_definitions'] = []
        for i, it in enumerate(related_definitions):
            # 合同链接1-3
            item['related_definitions'].append({'url': it.css('a::attr(href)').extract_first(),
                                                'title': it.css('a::text').extract_first()
                                                })

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