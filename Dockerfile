FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

%%writefile /content/scrapy_project/Dockerfile.splash
FROM scrapinghub/splash:3.5
EXPOSE 8051
CMD ["python3", "/app/bin/splash", "--port", "8051"]