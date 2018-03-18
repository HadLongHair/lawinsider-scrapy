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


class LawDictionaryScrapy(RedisSpider):
    name = 'law_dictionary'

    allowed_domains = ['www.lawinsider.com']
    # start_urls = ['https://www.lawinsider.com/dictionary/a']
    redis_key = 'dictionary:start_urls'
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
        papers = response.css('.col-lg-9.col-md-9.col-sm-12.col-xs-12 .paper')
        # Definition
        item['definition'] = []
        definition_list = []
        try:
            definitions = papers[0].css('ol li.snippet-content::text').extract()
            for definition in definitions:
                try:
                    definition_text = definition.replace('\n', '')
                    if definition_text:
                        definition_list.append(item['dictionary'] + definition_text)
                except Exception as e:
                    logging.error("No text", e)
        except:
            logging.error('No papers')

        item['definition'] = definition_list

        # examples
        item['example'] = []
        example_list = []
        try:
            examples = papers[1].css('ol li::text').extract()
            for example in examples:
                try:
                    example_text = example.replace('\n', '')
                    if example_text:
                        example_list.append(item['dictionary'] + example_text)
                except Exception as e:
                    logging.error("No example text", e)
        except:
            logging.error('No papers')

        item['example'] = example_list

        # Contract Tags TODO
        item['contract_tags'] = []
        contract_tag = {}
        try:
            contract_tags = papers[2].css('h3')
            contract_tags_text = papers[2]
            for i in contract_tags:
                contract_tag['name'] = i.css('a::text').extract_first()
                contract_tag['url'] = i.css('a::attr(href)').extract_first()
            for j in contract_tags_text:
                contract_tag['text'] = j.css('string::text').extract_first() + j.css('::text').extract_first()
        except:
            pass

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