import scrapy
from scrapy.loader import ItemLoader

from raiplayradio.items import Content, Episode, EpisodeLoader, Link


class Zapping(scrapy.Spider):
    name = "zapping"
    # TODO: check whether this can be parametrized
    start_urls = [
        "https://www.raiplayradio.it/programmi/zappingradio1/archivio/puntate/"
    ]

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
            ep_loader = EpisodeLoader(item=Episode(), selector=episode)
            ep_loader.add_css("title", "h3>a::text")
            ep_loader.add_css("updated", "span.canale::text")
            co_loader = ItemLoader(item=Content(), selector=episode)
            # loader.add_css("summary", "p::text")
            co_loader.add_css("cont", "p::text")
            co_loader.add_value("attr", {"type": "text"})
            ep_loader.add_value("content", co_loader.load_item())
            ep_loader.add_xpath("id", "@data-uniquename")
            img_url = response.urljoin(episode.xpath("@data-image").get())
            ep_loader.add_value("image", img_url)
            # ep.add_value(
            #     "link", Link(rel="related", href=img_url, type="image/jpeg",)
            # )
            item = ep_loader.load_item()

            request = scrapy.Request(
                episode.xpath("@data-mediapolis").get(),
                callback=self.resolve_media,
                meta={
                    "dont_redirect": True,
                    "handle_httpstatus_list": [302],
                    "original": item,
                },
                cb_kwargs=dict(loader=ep_loader),
            )
            yield request

    def resolve_media(self, response, loader):
        loader.add_value(
            "link",
            Link(
                rel="enclosure",
                href=response.headers.get("Location").decode("utf-8"),
                type="audio/mpeg",
            ),
        )

        yield loader.load_item()
