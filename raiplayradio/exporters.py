
"""
	<title>Example Feed</title>
	<subtitle>A subtitle.</subtitle>
	<link href="/feed" rel="self" />
    <link rel="self" type="application/atom+xml"
      href="http://example.org/feed.atom"/>
	<link href="http://example.org/" />
	<id>urn:uuid:60a76c80-d399-11d9-b91C-0003939e0af6</id>
	<updated>2003-12-13T18:30:02Z</updated>
    <entry>
		<title>Atom-Powered Robots Run Amok</title>
		<link href="http://example.org/2003/12/13/atom03" />
		<link rel="alternate" type="text/html" href="http://example.org/2003/12/13/atom03.html"/>
		<link rel="edit" href="http://example.org/2003/12/13/atom03/edit"/>
		<id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>
		<updated>2003-12-13T18:30:02Z</updated>
		<summary>Some text.</summary>
		<content type="xhtml">
			<div xmlns="http://www.w3.org/1999/xhtml">
				<p>This is the entry content.</p>
			</div>
		</content>
		<author>
			<name>John Doe</name>
			<email>johndoe@example.com</email>
		</author>
	</entry>

</feed>"""

from scrapy.exporters import XmlItemExporter
from scrapy.utils.python import is_listlike
from datetime import datetime

# ------------------------------------------------------------------------------------#
class AtomItemExporter(XmlItemExporter):
    # --------------------------------------------------------------------------------#
    def __init__(self, *args, **kwargs):
        kwargs["root_element"] = "feed"
        kwargs["item_element"] = "entry"

        now = datetime.now().isoformat(timespec="seconds")
        self.title = kwargs.pop("title", "Dummy")
        self.link = kwargs.pop("link", "http://dummy.site")
        self.url = kwargs.pop("url", "http://dummy.site/feed.atom")
        self.uuid = kwargs.pop("uuid", "random-uuid")
        self.description = kwargs.pop("description", "Dummy")
        self.updated = kwargs.pop("updated", now)

        super(AtomItemExporter, self).__init__(*args, **kwargs)
        self.indent = 2

    # --------------------------------------------------------------------------------#
    def _export_xml_field(self, name, serialized_value, depth, attrs=dict()):
        self._beautify_indent(depth=depth)
        self.xg.startElement(name, attrs)
        if hasattr(serialized_value, "items"):
            self._beautify_newline()
            for subname, value in serialized_value.items():
                self._export_xml_field(subname, value, depth=depth + 1)
            self._beautify_indent(depth=depth)
        elif is_listlike(serialized_value):
            self._beautify_newline()
            for value in serialized_value:
                self._export_xml_field("value", value, depth=depth + 1)
            self._beautify_indent(depth=depth)
        elif isinstance(serialized_value, str):
            self.xg.characters(serialized_value)
        else:
            self.xg.characters(str(serialized_value))
        self.xg.endElement(name)
        self._beautify_newline()

    # --------------------------------------------------------------------------------#
    def start_exporting(self):
        self.xg.startDocument()  # <?xml version="1.0" encoding="utf-8"?>
        self.xg.startElement(
            self.root_element, {"xmlns": "http://www.w3.org/2005/Atom"}
        )  # <feed xmlns="http://www.w3.org/2005/Atom">

        self._beautify_newline()  # \n
        # self._beautify_indent(1)  # 2 spaces, 1 indent

        self._export_xml_field("title", self.title, 2)
        self._export_xml_field(
            "link",
            self.link,
            2,
            attrs={"rel": "self", "type": "application/atom+xml", "href": self.url},
        )  # <link rel="self" type="application/atom+xml" href="<self.url>">
        self._export_xml_field("subtitle", self.description, 2)
        self._export_xml_field("updated", self.updated, 2)
        urn_id = "urn:uuid:" + self.uuid
        self._export_xml_field("id", urn_id, 2)

    # --------------------------------------------------------------------------------#
    def export_item(self, item):
        self._beautify_indent(2)
        self.xg.startElement(self.item_element, {})
        self._beautify_newline()
        for k, v in self._get_serialized_fields(item):
            if k == "enclosure":
                for enclosure in v:
                    attrs = dict(self._get_serialized_fields(enclosure))
                    self._beautify_indent(3)
                    self.xg.startElement("enclosure", attrs)
                    self.xg.endElement("enclosure")
                    self._beautify_newline()
            elif k == "content":
                self._beautify_indent(depth=3)
                self.xg.startElement("content:encoded", {})
                self.xg.ignorableWhitespace(v)
                self.xg.endElement("content:encoded")
                self._beautify_newline()
            else:
                self._export_xml_field(k, v, 3)
        self._beautify_indent(2)
        self.xg.endElement(self.item_element)
        self._beautify_newline()


class ZappingExporter(AtomItemExporter):
    def __init__(self, *args, **kwargs):
        kwargs["title"] = "Zapping Radio 1"
        kwargs["link"] = "https://www.raiplayradio.it/programmi/zappingradio1"
        kwargs["url"] = "https://dispenser.ovh/podcasts/zapping/feed.atom"
        kwargs["description"] = (
            "Conduce Giancarlo Loquenzi\n"
            "In redazione: Alessandro Allegra, Daniela Mecenate, Nicolò Randazzo e "
            "Valeria Riccioni\nRegia di Leonardo Patanè\n\n"
            "I fatti del giorno al ritmo dei titoli dei telegiornali italiani e stranieri, "
            "raccontati, commentati e discussi con ospiti e ascoltatori. Zapping Radio 1, "
            "tutte le notizie senza cambiare canale."
        )
        kwargs["uuid"] = "03ed583c-255e-4d63-9e32-ac6f2e1fddf8"
        super(ZappingExporter, self).__init__(*args, **kwargs)
