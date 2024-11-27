# Amazon Python Scrapy 🕸️
Python Scrapy spiders that scrape product data and reviews from [Amazon.com](https://www.amazon.com/). 

This Scrapy project contains 3 seperate spiders:

| Spider  |      Description      |
|----------|-------------|
| `amazon_search` |  Scrapes all product data from the Amazon product search page for a given list of keywords. | 
| `amazon_search_product` |  Crawls Amazon product search pages for a given list of keywords, then scrapes each individual product page. | 
| `amazon_reviews` |  Scrapes all Amazon product reviews from a list of product ASINs. | 

## ScrapeOps Proxy
This Amazon spider uses [ScrapeOps Proxy](https://scrapeops.io/proxy-aggregator/) as the proxy solution. ScrapeOps has a free plan that allows you to make up to 1,000 requests per month which makes it ideal for the development phase, but can be easily scaled up to millions of pages per month if needs be.

To use the ScrapeOps Proxy you need to first install the proxy middleware:

```python
pip install scrapeops-scrapy-proxy-sdk
```

Then activate the ScrapeOps Proxy by adding your API key to the `SCRAPEOPS_API_KEY` in the ``settings.py`` file.

```python
SCRAPEOPS_API_KEY = 'YOUR_API_KEY'
SCRAPEOPS_PROXY_ENABLED = True
DOWNLOADER_MIDDLEWARES = {
    'scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk': 725,
}
```

## ScrapeOps Monitoring
To monitor our scraper, this spider uses the [ScrapeOps Monitor](https://scrapeops.io/monitoring-scheduling/), a free monitoring tool specifically designed for web scraping. 

**Live demo here:** [ScrapeOps Demo](https://scrapeops.io/app/login/demo) 

![ScrapeOps Dashboard](https://scrapeops.io/assets/images/scrapeops-promo-286a59166d9f41db1c195f619aa36a06.png)

To use the ScrapeOps Proxy you need to first install the monitoring SDK:

```python
pip install scrapeops-scrapy
```

Then activate the ScrapeOps Proxy by adding your API key to the `SCRAPEOPS_API_KEY` in the ``settings.py`` file.

```python
SCRAPEOPS_API_KEY = 'YOUR_API_KEY'
# Add In The ScrapeOps Monitoring Extension
EXTENSIONS = {
'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500, 
}


DOWNLOADER_MIDDLEWARES = {

    ## ScrapeOps Monitor
    'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    
    ## Proxy Middleware
    'scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk': 725,
}
```

If you are using both the ScrapeOps Proxy & Monitoring then you just need to enter the API key once.

## Running The Scrapers
Make sure Scrapy and the ScrapeOps Monitor is installed:

```python
pip install scrapy scrapeops-scrapy
```

To run the Amazon spiders you should first set the search query parameters you want to search by updating the `keyword_list` list in the spiders:

```python
def start_requests(self):
    keyword_list = ['ipad']
    for keyword in keyword_list:
        amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page=1'
        yield scrapy.Request(url=amazon_search_url, callback=self.parse_search_results, meta={'keyword': keyword, 'page': 1})
```

Then to run the spider, enter one of the following command:

```
scrapy crawl amazon_search_product
```

### Configuring Amazon Product Search
To change the query parameters for the product search just change the keywords and locations in the `keyword_list` lists in the spider.

For example:

```python
def start_requests(self):
    keyword_list = ['ipad', 'laptops']
    for keyword in keyword_list:
        amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page=1'
        yield scrapy.Request(url=amazon_search_url, callback=self.parse_search_results, meta={'keyword': keyword, 'page': 1})
```

### Extract More/Different Data
Amazon product pages contain a lot of useful data, however, in this spider is configured to only parse some of the data. 

You can expand or change the data that gets extract by changing the yield statements:

```python
def parse_product_data(self, response):
    image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", response.text)[0])
    variant_data = re.findall(r'dimensionValuesDisplayData"\s*:\s* ({.+?}),\n', response.text)
    feature_bullets = [bullet.strip() for bullet in response.css("#feature-bullets li ::text").getall()]
    price = response.css('.a-price span[aria-hidden="true"] ::text').get("")
    if not price:
        price = response.css('.a-price .a-offscreen ::text').get("")
    yield {
        "name": response.css("#productTitle::text").get("").strip(),
        "price": price,
        "stars": response.css("i[data-hook=average-star-rating] ::text").get("").strip(),
        "rating_count": response.css("div[data-hook=total-review-count] ::text").get("").strip(),
        "feature_bullets": feature_bullets,
        "images": image_data,
        "variant_data": variant_data,
    }
```

### Speeding Up The Crawl
The spiders are set to only use 1 concurrent thread in the settings.py file as the ScrapeOps Free Proxy Plan only gives you 1 concurrent thread.

However, if you upgrade to a paid ScrapeOps Proxy plan you will have more concurrent threads. Then you can increase the concurrency limit in your scraper by updating the `CONCURRENT_REQUESTS` value in your ``settings.py`` file.

```python
# settings.py

CONCURRENT_REQUESTS = 10
```

### Storing Data
The spiders are set to save the scraped data into a CSV file and store it in a data folder using [Scrapy's Feed Export functionality](https://docs.scrapy.org/en/latest/topics/feed-exports.html).

```python
custom_settings = {
        'FEEDS': { 'data/%(name)s_%(time)s.csv': { 'format': 'csv',}}
        }
```

### Deactivating ScrapeOps Proxy & Monitor
To deactivate the ScrapeOps Proxy & Monitor simply comment out the follow code in your `settings.py` file:
