from dataclasses import dataclass, field
from datetime import datetime, timedelta
from queue import PriorityQueue
from typing import Any

from scrapy.extensions.feedexport import FeedExporter


@dataclass(order=True)
class TimelineItem:
    priority: timedelta
    item: Any = field(compare=False)


class TimelineExport(FeedExporter):
    def __init__(self, settings):  # , uri):
        # self.uri = uri
        self.now = datetime.now()
        self.queue = PriorityQueue()
        super().__init__(settings)

    def item_scraped(self, item, spider):
        td = self.now - item["updated"]
        self.queue.put(TimelineItem(priority=td, item=item,))
        return item

    def close_spider(self, spider):
        slot = self.slot
        while not self.queue.empty():
            item = self.queue.get().item
            slot.exporter.export_item(item)

        super().close_spider(spider)
