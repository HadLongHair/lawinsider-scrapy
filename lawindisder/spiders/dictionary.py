# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup as BS
from lawindisder.items import ClauseItem
from datetime import datetime


class LawClauseScrapy(scrapy.Spider):
    name = 'law_dictionary'

    allowed_domains = ['www.lawinsider.com']
    start_urls = ['https://www.lawinsider.com/dictionary/c']
    bases = 'https://www.lawinsider.com'

    def parse(self, response):
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
                item['dictionary'] = raw_dictionary.css('div.snippet-title span::text').extract().replace('\n', '')
            except:
                item['dictionary'] = None
                print('~Fail~')
            print('dictionary', ' ==================== > :', item['dictionary'], self.bases + item['url'])
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
        try:
            definitions = papers[0].css('ol li.snippet-content')
            item['definition'] = {'title': papers[0].css('h1::text').extract()}
            texts = []
            for definition in definitions:
                try:
                    definition_text = definition.css('li::text').extract().replace('\n', '')
                except:
                    definition_text = None
                    print("No text")
                texts.append(item['dictionary'] + definition_text)
            item['definition']['text'] = texts
        except:
            print('No papers')


        # related definitions
        related_definitions = response.css('.paper-sidebar .list-group .list-group-item a')
        item['related_definitions'] = []
        for i, it in enumerate(related_definitions):
            # 合同链接1-3
            print('related_definitions oooooooooooooooooooooo')
            item['related_definitions'].append({'url': it.css('a::attr(href)').extract_first(),
                                                'title': it.css('a::text').extract_first()
                                                })

        item['added_time'] = datetime.utcnow()
        item['latest_update'] = datetime.utcnow()
        yield item

        next_href = response.css('#pagination .next a::attr(href)')
        for n in next_href:
            if n:
                yield response.follow('https://www.lawinsider.com' + n.extract(), self.parse_detail)
            else:
                print('Next Clause Ref...')
                pass