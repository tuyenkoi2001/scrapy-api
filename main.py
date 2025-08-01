from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from books.spiders.media_spider import MediaSpider
import os
import json
import uuid
import logging
import crochet
import requests
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

crochet.setup()
app = FastAPI()
logging.basicConfig(level=logging.DEBUG)

@app.get("/")
@app.head("/")
async def root():
    return {"status": "API is running"}

@retry(stop=stop_after_attempt(12), wait=wait_fixed(5), retry=retry_if_exception_type(requests.exceptions.RequestException))
def check_splash():
    logging.debug("Checking Splash connection...")
    splash_urls = ["http://splash:8050", "http://splash.scrapinghub.com:8050/"]  # Thêm fallback
    for url in splash_urls:
        try:
            logging.debug(f"Trying Splash URL: {url}")
            response = requests.get(url, timeout=30)
            logging.debug(f"Splash response for {url}: {response.status_code}")
            if response.status_code == 200:
                return url
        except requests.exceptions.RequestException as e:
            logging.error(f"Splash connection attempt failed for {url}: {e}")
    logging.error("All Splash connection attempts failed")
    return None

@crochet.run_in_reactor
def run_spider(start_url: str, output_file: str):
    logging.debug(f"Starting spider for URL: {start_url}, Output: {output_file}")
    try:
        splash_url = check_splash()
        if not splash_url:
            logging.error("Cannot connect to Splash service, using direct Scrapy")
            settings = get_project_settings()
            settings.set('FEEDS', {f"/app/{output_file}": {'format': 'json'}}, priority='cmdline')
            settings.set('DOWNLOAD_TIMEOUT', 600)
            process = CrawlerProcess(settings)
            crawler = process.create_crawler(MediaSpider, start_url=start_url, use_splash=False)
            process.crawl(crawler)
            process.start()
        else:
            settings = get_project_settings()
            settings.set('FEEDS', {f"/app/{output_file}": {'format': 'json'}}, priority='cmdline')
            settings.set('SPLASH_URL', splash_url)
            settings.set('DOWNLOAD_TIMEOUT', 600)
            process = CrawlerProcess(settings)
            crawler = process.create_crawler(MediaSpider, start_url=start_url, use_splash=True)
            process.crawl(crawler)
            process.start()
    except Exception as e:
        logging.error(f"Spider failed: {e}")
        return

    logging.debug(f"Checking if file exists: /app/{output_file}")
    if os.path.exists(f"/app/{output_file}"):
        with open(f"/app/{output_file}", 'r') as f:
            data = json.load(f)
        logging.debug(f"File found: /app/{output_file}, Data: {data}")
    else:
        logging.error(f"File not found: /app/{output_file}")

def run_spider_task(start_url: str, output_file: str):
    eventual_result = run_spider(start_url, output_file)
    eventual_result.wait(timeout=600)

@app.post("/scrape")
async def scrape(url: str, background_tasks: BackgroundTasks):
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")
    
    output_file = f"output_{uuid.uuid4()}.json"
    logging.debug(f"Scrape request received for URL: {url}, Output: {output_file}")
    background_tasks.add_task(run_spider_task, url, output_file)
    return {
        "message": "Scraping started",
        "output_file": output_file,
        "url": url
    }

@app.get("/scrape")
async def scrape_get(url: str, background_tasks: BackgroundTasks):
    return await scrape(url, background_tasks)

@app.get("/results/{output_file}")
async def get_results(output_file: str):
    file_path = f"/app/{output_file}"
    logging.debug(f"Fetching results for: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"Results file not found: {file_path}")
        raise HTTPException(status_code=404, detail="Results file not found")
    with open(file_path, 'r') as f:
        results = json.load(f)
    logging.debug(f"Results retrieved: {results}")
    os.remove(file_path)
    logging.debug(f"Deleted file: {file_path}")
    return results