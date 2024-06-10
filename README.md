# Competiter-Pricing-Scraper
Crawl competitor pricing list and put into data lake

# How to add Pricing Crawler for new product(such as flyer, seal...)

## OverView
To add a product crawler, you need to create two modules:
- Crawler:
    Crawl (scrape) price information from the target URL and save it in AWS S3.
- Register:
    Receive the ByteStream output by Crawler (as lambda argument) and insert price records in google BigQuery.
    If the price changes from the previous time for the same spec and conditions (delivery date and number of copies),
    it also serves as a notification to Slack.

By implementing the non-instance method of the specified I/F, 
the two modules are transparently called from the lambda function.

## Crawler module
### module name
There are no strict naming conventions, 
please name it easy to identify the site name and the target product, such as printpac_seals_crawler.py

### implement
Implement a method with the following I/F that can be invoked on a non-instance.
Please refrain from using special libraries as it runs on lambda.

```
 def doCrawl(s3_bucketname:str, s3_subdir:str)->bool:
    """ 
        parameters
            s3_bucketname:str   - s3 buketname　for saving crawled data.
            s3_subdir:str       - s3 keyname such as "/price/my_crawl_data.json"
        
        returns
            bool - Success/failure (please keep a certain level of log output in the event of an error)
            
        descriptions
            - Implement up to the point where you acquire the target product data and save it to S3.
    """
```

And you also append to setting value to "global_settings.py".

```
from crawlers import ppac_seal_teikei

・・・

COMMAND_MAP:dict = {
 "ppac_seal_teikei" : ppac_seal_teikei,   
}

・・・

```

1. import your crawler module.
2. add "COMMAND_MAP" to invoke your module(doCrawl method).
     - key parameter: same name as your crawl moduke as string. that will be specified as a runtime parameter（payload） of lambda.
     - value parameter: your crawler moduke name.

### S3 file naming conventions

There are no rules regarding the format of file contents (Json format is recommended).
On the other hand, there are rules regarding file naming conventions, 
and if you do not follow them, your Register module will not be able to receive the correct byte stream.

the rule is very simple that is
1. In the first part of the file name, add an identifier that identifies the target site and product, separated by a hyphen.
2. In the second part of the file name, specify the save date and time separated by a hyphen.
3. Connect these two pieces of information with an underscore to create the file name.

In case of crawling seal-product pricing list from printpac(this is a raksul competitor in japan region).
S3 file name will be 
> printpac-seals-pricing_2024-06-10-120030.json

## Register module

