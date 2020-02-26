# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import xml.sax.saxutils
from datetime import datetime

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, Identity, MapCompose, TakeFirst


def parse_date(self, values):
    for value in values:
        yield datetime.strptime(value, "%d/%m/%Y")


def parse_id(self, values):
    for value in values:
        yield value.split("-", 1)[1]


# def serialize_date(value):
#     return value.astimezone().isoformat()


def serialize_id(value):
    return "urn:uuid:" + str(value)


class EpisodeLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    date_in = parse_date
    guid_in = parse_id
    content_in = Identity()
    link_in = Identity()
    link_out = Identity()
    enclosure_in = Identity()
    enclosure_out = Identity()


class Link(scrapy.Item):
    rel = scrapy.Field()
    href = scrapy.Field()
    type = scrapy.Field()


class Enclosure(scrapy.Item):
    url = scrapy.Field()
    type = scrapy.Field()


class Episode(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    guid = scrapy.Field(serializer=serialize_id)
    enclosure = scrapy.Field()
    # date = scrapy.Field(serializer=serialize_date)  # serializer= print UTC date
    date = scrapy.Field()
    description = scrapy.Field(
        input_processor=MapCompose(str.strip, xml.sax.saxutils.escape),
    )
    image = scrapy.Field()
