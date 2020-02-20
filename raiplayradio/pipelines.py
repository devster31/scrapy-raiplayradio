# -*- coding: utf-8 -*-

import re
from datetime import datetime
from queue import PriorityQueue
from sys import stdout

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy

from raiplayradio.exporters import ZappingExporter


class RaiplayRadioPipeline(object):
    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        pass


class AtomExportPipeline(object):
    def process_item(self, item, spider):
        exp = ZappingExporter(stdout)
        exp.export_item(item)
        return item


class DateFixPipeline(object):
    def process_item(self, item, spider):
        if not item["updated"]:
            date = re.match(r".*(?P<date>\d{2}\/\d{2}\/\d{4}).*", item["title"]).group(
                "date"
            )
            item["updated"] = datetime.strptime(date, "%d/%m/%Y")
        return item
