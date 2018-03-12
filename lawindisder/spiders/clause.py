# -*- coding: utf-8 -*-
import scrapy
from lawindisder.items import ClauseItem
from datetime import datetime


class LawClauseScrapy(scrapy.Spider):
    name = 'law_clause'

    allowed_domains = ['www.lawinsider.com']
    start_urls = ['https://www.lawinsider.com/clauses/a']
    bases = 'https://www.lawinsider.com'

    def parse(self, response):
        # follow links to detail pages
        detail_list_urls = response.css('.list-group-item.dynamic-linkset.col-lg-6.col-sm-12.col-xs-12.col-md-6::attr(href)')

        raw_clause = response.css('.dynamic-linkset.list-group-item')
        # assert 1 == 2
        for i, list_url in enumerate(detail_list_urls):
            # print('poi~')
            item = ClauseItem()
            # item['referer'] = response.request.headers.get('Referer', None).decode('utf-8')
            item['url'] = list_url.extract()
            try:
                item['clause'] = raw_clause[i].css('a::text').extract()[1].replace('\n', '')
            except:
                item['clause'] = None
                print('~Fail~')
            print('clause', ' ==================== > :', item['clause'])
            request = scrapy.Request(self.bases + list_url.extract(), callback=self.parse_detail)
            request.meta['item'] = item
            # request.meta['proxy'] = 'http://crystal.ge:9svqswvf@117.48.199.217:16818'
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

        # related clause
        related_clauses = response.css('#sidebar-related-clauses .list-group-item a')
        item['related_clauses'] = []
        for i, it in enumerate(related_clauses):
            # 合同链接1-3
            item['related_clauses'].append({'url': it.css('a::attr(href)').extract_first(),
                                            'title': it.css('a::text').extract_first()
                                            })
        # related contacts
        related_contacts = response.css('#sidebar-related-contracts-by-clause .list-group-item a')
        item['related_contracts'] = []
        for i, it in enumerate(related_contacts):
            # 合同链接1-3
            item['related_contracts'].append({'url': it.css('a::attr(href)').extract_first(),
                                              'title': it.css('a::text').extract_first()
                                              })

        # parent clause
        parent_clauses = response.css('#sidebar-parent-clauses .list-group-item a')
        item['parent_clauses'] = []
        for i, it in enumerate(parent_clauses):
            # 合同链接1-3
            item['parent_clauses'].append({'url': it.css('a::attr(href)').extract_first(),
                                           'title': it.css('a::text').extract_first()
                                           })

        # sub clause
        sub_clauses = response.css('#sidebar-child-clauses .list-group-item a')
        item['sub_clauses'] = []
        for i, it in enumerate(sub_clauses):
            # 合同链接1-3
            item['sub_clauses'].append({'url': it.css('a::attr(href)').extract_first(),
                                        'title': it.css('a::text').extract_first()
                                        })

            # 所有修改版本链接
            # if cs.css('.all-variations-btn a'):
            #     try:
            #         variations = cs.css('.all-variations-btn a')[0]
            #         item['variations_url'] = contract_url_4.css('a::attr(href)').extract_first()
            #         item['variations_title'] = contract_url_4.css('a::text').extract_first()
            #     except:
            #         print('Error Log')

        clause_snippet = response.css('.list-group-item.clause-snippet')
        # ref
        for cs in clause_snippet:
            try:
                clauses_text = cs.css('.snippet-content::text').extract()[1].replace('\n', '')
            except:
                clauses_text = None
                print("No text")
            item['clauses_text'] = item['clause'] + clauses_text

            # 合同样例
            instance_tags = cs.css('.instance-tag a')
            item['sample_contracts'] = []
            for i, it in enumerate(instance_tags):
                # 合同链接1-3
                item['sample_contracts'].append({'url': it.css('a::attr(href)').extract_first(),
                                                 'title': it.css('a::text').extract_first()
                                                 })

            item['added_time'] = datetime.utcnow()
            item['latest_update'] = datetime.utcnow()
            yield item

        next_href = response.css('#pagination .next a::attr(href)')
        for n in next_href:
            if n:
                # response.meta['proxy'] = 'http://crystal.ge:9svqswvf@117.48.199.217:16818'
                yield response.follow('https://www.lawinsider.com' + n.extract(), self.parse_detail)
            else:
                print('Next Clause Ref...')
                pass