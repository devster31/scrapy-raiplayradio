import scrapy
from raiplayradio.items import Episode, EpisodeLoader


class Zapping(scrapy.Spider):
    name = "zapping"
    start_urls = [
        "https://www.raiplayradio.it/programmi/zappingradio1/archivio/puntate/"
    ]
    cur_page = int()
    cur_season = int()
    pages = []
    seasons = []

    def parse(self, response):
        seasons = [
            dict(
                {
                    "url": season.css("::attr(href)").get(),
                    "season": int(season.css("::text").re(r"(\d{4})")[0]),
                }
            )
            for season in response.css("ul.listaStagioniPuntate>li>a")
        ]

        for season in seasons:
            yield response.follow(season["url"], callback=self.parse_pages)

    def parse_pages(self, response):
        pages = [
            dict(
                {
                    "url": page.css("::attr(href)").get(),
                    "page": int(page.css("::text").re(r"(\d{1,})")[0]),
                }
            )
            for page in response.css("ul.pagination>li>a")
        ]

        for page in pages:
            yield response.follow(page["url"], callback=self.parse_episodes)

    def parse_episodes(self, response):
        for episode in response.css(".archivioPuntate").css("div.row.listaAudio"):
            ep = EpisodeLoader(item=Episode(), selector=episode)
            ep.add_css("title", "h3>a::text")
            ep.add_css("date", "span.canale::text")
            ep.add_css("description", "p::text")
            ep.add_xpath("uuid", "@data-uniquename")
            img_url = response.urljoin(episode.xpath("@data-image").get())
            ep.add_value("image", img_url)
            item = ep.load_item()

            request = scrapy.Request(
                episode.xpath("@data-mediapolis").get(),
                callback=self.resolve_media,
                meta={
                    "dont_redirect": True,
                    "handle_httpstatus_list": [302],
                    "original": item,
                },
                cb_kwargs=dict(original=item),
            )
            yield request

    def resolve_media(self, response, original):
        item = original
        item["url"] = response.headers.get("Location").decode("utf-8")
        yield item
