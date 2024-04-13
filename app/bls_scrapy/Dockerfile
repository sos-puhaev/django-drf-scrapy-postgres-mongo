FROM python:3.8-slim
RUN apt-get update && apt-get install -y libpq-dev
RUN pip3 install scrapy psycopg2-binary pymongo
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
WORKDIR /app/bls_scrapy/
COPY . /app/bls_scrapy