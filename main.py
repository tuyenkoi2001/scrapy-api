from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from books.spiders.media_spider import MediaSpider
import os
import json
import uuid
from urllib.parse import urlparse
import logging
import crochet

crochet.setup()  # Khởi tạo crochet

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)

@app.get("/")
@app.head("/")
async def root():
    return {"status": "API is running"}

@crochet.run_in_reactor
def run_spider(start_url: str, output_file: str):
    logging.debug(f"Starting spider for URL: {start_url}, Output: {output_file}")
    settings = get_project_settings()
    settings.set('FEEDS', {f"/app/{output_file}": {'format': 'json'}}, priority='cmdline')
    process = CrawlerProcess(settings)
    process.crawl(MediaSpider, start_url=start_url)
    process.start()
    logging.debug(f"Checking if file exists: /app/{output_file}")
    if os.path.exists(f"/app/{output_file}"):
        with open(f"/app/{output_file}", 'r') as f:
            data = json.load(f)
        logging.debug(f"File found: /app/{output_file}, Data: {data}")
        return data
    logging.error(f"File not found: /app/{output_file}")
    return []

@app.post("/scrape")
async def scrape(url: str, background_tasks: BackgroundTasks):
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")
    
    output_file = f"output_{uuid.uuid4()}.json"
    logging.debug(f"Scrape request received for URL: {url}, Output: {output_file}")
    background_tasks.add_task(run_spider, url, output_file)
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
    os.remove(file_path)  # Xóa file sau khi đọc
    logging.debug(f"Deleted file: {file_path}")
    return results