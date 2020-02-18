# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.exceptions import DropItem


class RaiplayRadioPipeline(object):
    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        if item.get("location"):
            return item

        self.crawler.engine.crawl(
            scrapy.Request(
                item["url"],
                callback=self.add_location,
                meta={
                    "dont_redirect": True,
                    "handle_httpstatus_list": [302],
                    "original": item,
                },
            ),
            spider,
        )

        # todo: seems inefficient
        # you have to drop the item, and send it again after your check
        raise DropItem()

    def add_location(self, response):
        item = response.meta["original"]
        item["location"] = response.headers.get("Location").decode("utf-8")
        yield item
