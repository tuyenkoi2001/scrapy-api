from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from books.spiders.media_spider import MediaSpider
import os
import json
import uuid
from urllib.parse import urlparse

app = FastAPI()

@app.get("/")
@app.head("/")  # Thêm hỗ trợ phương thức HEAD
async def root():
    return {"status": "API is running"}

def run_spider(start_url: str, output_file: str):
    settings = get_project_settings()
    settings.set('FEEDS', {output_file: {'format': 'json'}}, priority='cmdline')
    process = CrawlerProcess(settings)
    process.crawl(MediaSpider, start_url=start_url)
    process.start()
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            return json.load(f)
    return []

@app.post("/scrape")
async def scrape(url: str, background_tasks: BackgroundTasks):
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")
    
    output_file = f"output_{uuid.uuid4()}.json"
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
    file_path = f"{output_file}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Results file not found")
    with open(file_path, 'r') as f:
        results = json.load(f)
    return results