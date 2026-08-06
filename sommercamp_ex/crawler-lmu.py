# Hier importieren wir die benötigten Softwarebibliotheken.
import hashlib
from resiliparse.extract.html2text import extract_plain_text
from scrapy import Spider, Request
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http.response.html import HtmlResponse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class SeleniumMiddleware:
    def __init__(self):
        opts = Options()
        opts.add_argument("--healess=new")
        self.driver = webdriver.Firefox(options=opts)

    @classmethod
    def from_crawler(cls, crawler):
        mw = cls()
        crawler.signals.connect(mw.spider_closed, signal=signals.spider_closed)
        return mw

    def process_request(self, request, spider):
        if request.url.endswith("/robots.txt"):
            return None

        self.driver.get(request.url)
        time.sleep(2)
        return HtmlResponse(
            url=self.driver.current_url,
            body=self.driver.page_source,
            encoding="utf-8",
            request=request,
        )
    
    def spider_closed(self):
        self.driver.quit()

class SchoolSpider(Spider):
    # Gib hier dem ſCrawler einen eindeutigen Name,
    # der beschreibt, was du crawlst.
    name = "school"

    start_urls = [
        # Gib hier mindestens eine (oder mehrere) URLs an,
        # bei denen der Crawler anfangen soll,
        # Seiten zu downloaden.
        "https://community.lemansultimate.com/index.php",
    ]
    link_extractor = LxmlLinkExtractor(
        # Beschränke den Crawler, nur Links zu verfolgen,
        # die auf eine der gelisteten Domains verweisen.
        allow_domains=["community.lemansultimate.com"]
    )
    custom_settings = {
        # Identifiziere den Crawler gegenüber den gecrawlten Seiten.
        "USER_AGENT": "Sommercamp (https://uni-jena.de)",
        # Der Crawler soll nur Seiten crawlen, die das auch erlauben.
        "ROBOTSTXT_OBEY": True,
        # Frage zu jeder Zeit höchstens 4 Webseiten gleichzeitig an.
        "CONCURRENT_REQUESTS": 1,
        # Verlangsame den Crawler, wenn Webseiten angeben,
        # dass sie zu oft angefragt werden.
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1,
        # Frage nicht zwei mal die selbe Seite an.
        "HTTPCACHE_ENABLED": False,
        "DOWNLOADER_MIDDLEWARES": {SeleniumMiddleware: 543},
    }

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            #driver = webdriver.Firefox();
            #driver.get("start_url");
            #"docno": str(hash(response.url));
            #"url": response.url;
            #"title": response.css("title::text").get();
            #"text": extract_plain_text(response.text, main_content=True);
            return
        
        # Speichere die Webseite als ein Dokument in unserer Dokumentensammlung.
        yield {
            # Eine eindeutige Identifikations-Nummer für das Dokument.
            "docno": str(hash(response.url)),
            # Die URL der Webseite.
            "url": response.url,
            # Der Titel der Webseite aus dem <title> Tag im HTML-Code.
            "title": response.css("title::text").get(),
            # Der Text der Webseite.
            # Um den Hauptinhalt zu extrahieren, benutzen wir
            # eine externe Bibliothek.
            "text": extract_plain_text(response.text, main_content=True),
        }

        # Finde alle Links auf der aktuell betrachteten Webseite.
        for link in self.link_extractor.extract_links(response):
            if link.text == "":
                # Ignoriere Links ohne Linktext, z.B. bei Bildern.
                continue
            # Für jeden gefundenen Link, stelle eine Anfrage zum Crawling.
            yield ReVquest(link.url, callback=self.parse)