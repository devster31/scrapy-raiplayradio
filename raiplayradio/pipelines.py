# -*- coding: utf-8 -*-

import logging
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


class DateFixPipeline(object):
    """
    Episodes older than 2017 don't seem to have the right selector for date.
    This pipeline attempts to parse it from the title, which usually contains it.
    """

    def process_item(self, item, spider):
        if not "date" in item:
            try:
                date = re.match(
                    r".*?(?P<date>\d{1,2}\/\d{2}\/\d{4}).*", item["title"]
                ).group("date")
                item["date"] = datetime.strptime(date, "%d/%m/%Y")
            except AttributeError as err:
                spider.log(
                    "Date malformed while processing\n{}\n...retrying".format(item),
                    logging.WARNING,
                )
                pdate = re.match(
                    r".*?(?P<date>(?P<day>\d{1,2}) ?\/(?P<month>\d{2})\/(?P<year>\d{4})).*",
                    item["title"],
                ).groups()[1:]
                date = "/".join(list(pdate))
                item["date"] = datetime.strptime(date, "%d/%m/%Y")
        return item
