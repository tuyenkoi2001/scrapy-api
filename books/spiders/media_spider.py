import scrapy
from scrapy_splash import SplashRequest
from scrapy.pipelines.images import ImagesPipeline
from urllib.parse import urlparse

class MediaSpider(scrapy.Spider):
    name = "media"

    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []
        self.allowed_domains = [urlparse(start_url).netloc] if start_url else []

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 2.0})

    def parse(self, response):
        for img in response.css('img::attr(src)').getall():
            if img:
                image_url = response.urljoin(img)
                yield {
                    'image_urls': [image_url],
                    'source_url': response.url,
                }

        # Theo dõi các liên kết để tìm thêm hình ảnh (tùy chọn)
        for next_page in response.css('a::attr(href)').getall():
            next_page_url = response.urljoin(next_page)
            if next_page_url.startswith(self.start_urls[0]):  # Chỉ theo dõi liên kết trong cùng domain
                yield SplashRequest(next_page_url, self.parse, args={'wait': 2.0})

class CustomImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        url = item.get('source_url', 'unknown')
        domain = urlparse(url).netloc.replace('.', '_')
        image_guid = request.url.split('/')[-1]
        return f'images/{domain}_{image_guid}'