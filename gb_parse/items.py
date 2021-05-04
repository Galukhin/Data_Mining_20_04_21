# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    img_links = scrapy.Field()
    specifications = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
