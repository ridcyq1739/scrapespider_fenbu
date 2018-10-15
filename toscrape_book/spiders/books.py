# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy.linkextractors import LinkExtractor
from ..items import BookItem


class BooksSpider(RedisSpider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    #start_urls = ['http://books.toscrape.com/']

    # 书籍列表页面的解析函数
    def parse(self, response):
        links = response.css('article.product_pod h3 a::attr(href)').extract()
        for link in links:
            link = response.urljoin(link)
            yield scrapy.Request(link, callback=self.parse_book)

        next_url = response.css('ul.pager li.next a::attr(href)').extract_first()
        if next_url:
            next_url = response.urljoin(next_url)
            yield scrapy.Request(next_url, callback=self.parse)

    # 书籍页面的解析函数
    def parse_book(self,response):
        book = BookItem()
        sel = response.css('div.product_main')
        book['name'] = sel.xpath('./h1/text()').extract_first()
        book['price'] = sel.css('p.price_color::text').extract_first()
        book['review_rating'] = sel.css('p.star-rating::attr(class)').re_first('star-rating ([a-zA-Z]+)')

        sel = response.css('table.table.table-striped')
        book['upc'] = sel.xpath('(.//tr)[1]/td/text()').extract_first()
        book['stock'] = sel.xpath('(.//tr)[last()-1]/td/text()').re_first('\((\d+) available\)')
        book['review_num'] = sel.xpath('(.//tr)[last()] / td / text()').extract_first()

        yield book