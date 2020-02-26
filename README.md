# scrapy-raiplayradio

### Basic usage
```
python3 -m scrapy crawl zapping -o "emptyfile:///tmp/feed.rss" -t zapping
```
spiders are show-specific as `start_url` is defined in the file as well as exporters
as show-specific details are hardcoded

### Comments
basic settings add an `rss` and `<show>` exporter, force `FEED_STORE_EMPTY = True`
and replace the `FeedExporter` extension class with another class which accumulates
in a `PriorityQueue` ordered by `<now> - <date of episode>` and exports them in
reverse chronological order