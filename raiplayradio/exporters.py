import os
from datetime import datetime

from scrapy.exporters import XmlItemExporter
from scrapy.extensions.feedexport import FileFeedStorage
from scrapy.utils.python import is_listlike
from w3lib.url import file_uri_to_path
from xml.sax.saxutils import XMLGenerator


class RssItemExporter(XmlItemExporter):
    """Adapted from https://github.com/ljanyst/scrapy-rss-exporter
    """

    def __init__(self, file, *args, **kwargs):
        kwargs["root_element"] = "rss"
        kwargs["item_element"] = "item"
        self.channel_element = "channel"
        self.date_format = "%a, %d %b %Y %H:%M:%S %z"

        now = datetime.now().astimezone().strftime(self.date_format)
        self.title = kwargs.pop("title", "Dummy Channel")
        self.link = kwargs.pop("link", "http://dummy.site")
        self.description = kwargs.pop("description", "Dummy Description")
        self.language = kwargs.pop("language", "en-us")
        self.build_date = kwargs.pop("pub_date", now)
        self.category = kwargs.pop("category", None)
        self.author = kwargs.pop("author", None)
        self.pod_image = kwargs.pop("image", None)

        super().__init__(file, *args, **kwargs)
        self.xg = XMLGenerator(file, encoding=self.encoding, short_empty_elements=True)
        self.indent = 2
        self.indent = 2

    def start_exporting(self):
        self.xg.startDocument()
        self.xg.startElement(
            self.root_element,
            {
                "version": "2.0",
                "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
                "xmlns:media": "http://search.yahoo.com/mrss/",
                "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
            },
        )
        self._beautify_newline()
        self._beautify_indent(1)
        self.xg.startElement(self.channel_element, {})
        self._beautify_newline()

        self._export_xml_field("title", self.title, 2)
        self._export_xml_field("link", self.link, 2)
        self._export_xml_field("description", self.description, 2)
        self._export_xml_field("pubDate", self.build_date, 2)
        self._export_xml_field("lastBuildDate", self.build_date, 2)
        if self.category is not None:
            for t in self.category:
                self._beautify_indent(2)
                self.xg.startElement("itunes:category", {"text": t})
                self.xg.endElement("itunes:category")
                self._beautify_newline()
        if self.author is not None:
            self._beautify_indent(2)
            self.xg.startElement("itunes:author", {})
            self._xg_characters(str(self.author))
            self.xg.endElement("itunes:author")
            self._beautify_newline()
        if self.pod_image is not None:
            self._beautify_indent(2)
            self.xg.startElement("image", {})
            self._beautify_newline()
            self._export_xml_field("url", self.pod_image, 3)
            self._beautify_indent(2)
            self.xg.endElement("image")
            self._beautify_newline()

    def export_item(self, item):
        self._beautify_indent(2)
        self.xg.startElement(self.item_element, {})
        self._beautify_newline()
        for k, v in self._get_serialized_fields(item):
            if k == "enclosure":
                for enclosure in v:
                    attrs = dict(self._get_serialized_fields(enclosure))
                    if "length" not in attrs:
                        attrs["length"] = "0"
                    self._beautify_indent(3)
                    self.xg.startElement("enclosure", attrs)
                    self.xg.endElement("enclosure")
                    self._beautify_newline()
            elif k == "link":
                for link in v:
                    self._beautify_indent(3)
                    self.xg.startElement("link", {})
                    self._xg_characters(str(link))
                    self.xg.endElement("link")
                    self._beautify_newline()
            elif k == "image":
                self._beautify_indent(3)
                self.xg.startElement("media:thumbnail", {"url": v})
                self.xg.endElement("media:thumbnail")
                self._beautify_newline()
                self._beautify_indent(3)
                self.xg.startElement("itunes:image", {"href": v})
                self.xg.endElement("itunes:image")
                self._beautify_newline()
            elif k == "date":
                self._beautify_indent(3)
                self.xg.startElement("pubDate", {})
                self._xg_characters(v.astimezone().strftime(self.date_format))
                self.xg.endElement("pubDate")
                self._beautify_newline()
            else:
                self._export_xml_field(k, v, 3)
        self._beautify_indent(2)
        self.xg.endElement(self.item_element)
        self._beautify_newline()

    def finish_exporting(self):
        self._beautify_indent(1)
        self.xg.endElement(self.channel_element)
        self._beautify_newline()
        self.xg.endElement(self.root_element)
        self.xg.endDocument()


class ZappingExporter(RssItemExporter):
    def __init__(self, *args, **kwargs):
        # TODO: parametrize or scrape possible?
        kwargs["title"] = "Zapping Radio 1"
        kwargs["link"] = "https://www.raiplayradio.it/programmi/zappingradio1"
        kwargs["description"] = (
            "Conduce Giancarlo Loquenzi\n"
            "In redazione: Alessandro Allegra, Daniela Mecenate, Nicolò Randazzo e "
            "Valeria Riccioni\nRegia di Leonardo Patanè\n\n"
            "I fatti del giorno al ritmo dei titoli dei telegiornali italiani e stranieri, "
            "raccontati, commentati e discussi con ospiti e ascoltatori. Zapping Radio 1, "
            "tutte le notizie senza cambiare canale."
        )
        kwargs["language"] = "it-it"
        kwargs["category"] = ["News"]
        kwargs["author"] = "Rai Radio 1"
        kwargs[
            "image"
        ] = "https://www.raiplayradio.it/cropgd/252x252/dl/img/2017/12/14/1513257688023_15-radio1-zapping-01.jpg"
        super().__init__(*args, **kwargs)


class EmptyFileFeedStorage(FileFeedStorage):
    def open(self, spider):
        dirname = os.path.dirname(self.path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        return open(self.path, "wb")
