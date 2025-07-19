BOT_NAME = 'books'

SPIDER_MODULES = ['books.spiders']
NEWSPIDER_MODULE = 'books.spiders'

ITEM_PIPELINES = {
    'books.spiders.media_spider.CustomImagesPipeline': 1,
}

IMAGES_STORE = 'images'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

ROBOTSTXT_OBEY = False

SPLASH_URL = 'http://splash:8050'  # Địa chỉ container Splash trên Render