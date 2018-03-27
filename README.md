# README #

Lawinsider 爬虫,包括dictionary,clause,contract

### TODO ###

* 1.增量抓取
* 2.断点爬取
* 3.分布式

### 注意 ###

1.代码拉下来后,setting.py文件,修改数据库相关信息,以及pipeline.py文件的<collection_name>,配置mongodb的collection
2.<spider>.py文件的<start_url>需要进行修改,如果用Redisspider的话,则启用<redis_key>,注释掉<start_url>变量

### 运行 ###
1.项目根目录下:
scrapy crawl <spider name>
2.spider目录下(Redisspider):
scrapy runspider <spider>.py