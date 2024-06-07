# Competiter-Pricing-Scraper
Crawl competitor pricing list and put into data lake

# How to add Pricing Crawler for new product(such as flyer, seal...)

## OverView
To add a product crawler, you need to create two modules:
- Crawler
    Crawl (scrape) price information from the target URL and save it in AWS S3.
- Register
    Receive the ByteStream output by Crawler (as lambda argument) and insert price records in google BigQuery.
    If the price changes from the previous time for the same spec and conditions (delivery date and number of copies),
    it also serves as a notification to Slack.

By implementing the non-instance method of the specified I/F, 
the two modules are transparently called from the lambda function.

## Crawler module
### module name
There are no strict naming conventions, 
please name it easy to identify the site name and the target product, such as printpac_seals_crawler.py
