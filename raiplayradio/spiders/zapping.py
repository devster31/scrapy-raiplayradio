# -*- coding: utf-8 -*-

import scrapy

from raiplayradio.items import Episode, EpisodeLoader, Enclosure, Link


class Zapping(scrapy.Spider):
    name = "zapping"
    # TODO: check whether this can be parametrized
    start_urls = [
        "https://www.raiplayradio.it/programmi/zappingradio1/archivio/puntate/"
    ]
    podcast_uuid = str()

    def parse(self, response):
        self.podcast_uuid = response.xpath("body/@data-id").get().split("-", 1)[1]

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
            link = response.urljoin(episode.xpath("@data-href").get())
            ep_loader.add_value("link", link)
            # ep_loader.add_xpath("guid", "@data-uniquename")
            ep_loader.add_value("guid", link)
            ep_loader.add_css("date", "span.canale::text")
            ep_loader.add_css("description", "p::text")
            img_url = response.urljoin(episode.xpath("@data-image").get())
            ep_loader.add_value("image", img_url)
            item = ep_loader.load_item()

            request = scrapy.Request(
                episode.xpath("@data-mediapolis").get(),
                callback=self.resolve_media,
                meta={"dont_redirect": True, "handle_httpstatus_list": [302]},
                cb_kwargs=dict(loader=ep_loader),
            )
            yield request

    def resolve_media(self, response, loader):
        loader.add_value(
            "enclosure",
            Enclosure(
                url=response.headers.get("Location").decode("utf-8"), type="audio/mpeg",
            ),
        )

        yield loader.load_item()
