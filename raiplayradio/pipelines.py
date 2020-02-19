# -*- coding: utf-8 -*-

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from queue import PriorityQueue
from sys import stdout
from typing import Any

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
        pass


@dataclass(order=True)
class TimelineItem:
    priority: timedelta
    item: Any = field(compare=False)


class TimelineExportPipeline(object):
    def __init__(self, uri):
        self.uri = uri
        self.now = datetime.now()
        self.queue = PriorityQueue()

    #     self.queue = PriorityQueue()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(uri=crawler.settings.get("FEED_URI"))

    def process_item(self, item, spider):
        try:
            td = self.now - item["updated"]
        except KeyError:
            date = re.match(
                r".*(?P<date>\d{2}\/\d{2}\/\d{4}).*", item["title"]
            ).group("date")
            item["updated"] = datetime.strptime(date, "%d/%m/%Y")
            td = self.now - item["updated"]
        self.queue.put(TimelineItem(priority=td, item=item,))
        return item

    def open_spider(self, spider):
        f = open(self.uri, "wb")
        self.exporter = ZappingExporter(f)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        while not self.queue.empty():
            item = self.queue.get().item
            self.exporter.export_item(item)

        self.exporter.finish_exporting()
