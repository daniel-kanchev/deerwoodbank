import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from deerwoodbank.items import Article


class deerwoodbankSpider(scrapy.Spider):
    name = 'deerwoodbank'
    start_urls = ['https://deerwoodbank.com/blog/']

    def parse(self, response):
        links = response.xpath('//h3/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//span[@class="page"]/a/@href').getall()
        yield from response.follow_all(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@id="media-page-top"]/p/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@id="media-page-top"]/p[2]/text()').get()
        if date:
            date = " ".join(date.split()[:3])

        content = response.xpath('//div[@id="media-page"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
