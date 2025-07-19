BOT_NAME = 'books'
SPIDER_MODULES = ['books.spiders']
NEWSPIDER_MODULE = 'books.spiders'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
ROBOTSTXT_OBEY = False
SPLASH_URL = 'http://splash:8051'
DOWNLOAD_TIMEOUT = 600
SPLASH_TIMEOUT = 120
RETRY_TIMES = 15
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]
DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'