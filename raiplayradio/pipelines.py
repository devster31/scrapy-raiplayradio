# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from sys import stdout
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
