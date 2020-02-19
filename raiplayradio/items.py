# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

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


def serialize_date(value):
    return value.date().isoformat()


def serialize_id(value):
    return "urn:uuid:" + str(value)


class EpisodeLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    updated_in = parse_date
    id_in = parse_id


class Episode(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    updated = scrapy.Field(serializer=serialize_date)  # serializer= print UTC date
    description = scrapy.Field()
    image = scrapy.Field()
    id = scrapy.Field(serializer=serialize_id)
