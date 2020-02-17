import scrapy


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
            yield {
                "title": episode.css("h3>a::text").get(),
                "url": episode.xpath("@data-mediapolis").get(),
                "date": episode.css("span.canale::text").get(),
                "desc": episode.css("p::text").get().strip(),
                "image": response.urljoin(episode.xpath("@data-image").get()),
            }
