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
     - value parameter: your crawler module name.

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

The general flow is the same as the Crawler module, 
but since there is data registration in BigQuery and Slack notifications, you need to import and use those modules appropriately.

### module name
There are no strict naming conventions, 
please name it easy to identify the site name and the target product, such as printpac_seals_register.py

### implement
Implement a method with the following I/F that can be invoked on a non-instance.
Please refrain from using special libraries as it runs on lambda.

```
def doRegist(data:bytes)->bool:
    """ 
        parameters
            data:bytes - recieve byte stream that crawler module save in S3 by AWS S3 event bridge
    
        returns
            boole - Success/failure (please keep a certain level of log output in the event of an error)
        
        descriptions
            - Implement the process up to inputting the Crawled data into BigQuery.
            - To implement it, you need to use some built-in libraries.
            - Please proceed with implementation using Mock as appropriate, or check operation in your company's Slack or Bigquery environment.
    """
```

And you also append to setting value to "global_settings.py".

```
from registers import ppac_seal_teikei_reg

・・・

FILE_PREFIX_MAP:dict = {
 "printpack-seal-teikei" : ppac_seal_teikei_reg,   
}

・・・
```

1. import your register module.
2. add "FILE_PREFIX_MAP" to invoke your module(doRegist method).
     - key parameter: same name as target s3 filename's first part as string.
       - exam: if filename is "printpac-seals-pricing_2024-10-10-120000.json" then, key name is "printpac-seals-prising".
     - value parameter: your register module name.

### slack.py

It was lightly wrapped Slack message sending api. 
By changing the constant SLACK_WEBHOOK_URL in global_setting.py, you can run it in your own environment for development and testing.

```
def notify(text):
    """ 
        Parameters
            text: message
    """
```

### bq_manager.py

Use the following two methods（this module must be instantiated for use）.

```
def persist_from_jsonlist(self, target_name:str, rows:list):
    """ Register data from Json to BigQuery
        Parameters:
            target_name     : [project_id].[dataset_id].[table_id] for BigQuery
            rows            : List<Json(dict)>
    """

def get_day_diff(self, target_name:str, concat_cols:str, partition_key:str, date_key:str, price_key:str, old_price_col_name:str, target_date:str)->bigquery.table.RowIterator:
    """ Add and return the previous day's price column according to the specified information
        Parameters:
            target_name     : [project_id].[dataset_id].[table_id] for BigQuery
            concat_cols     : 　Define the information you want to obtain in one column ⇒ Exam：CONCAT(shape, '-' , unit, '-', eigyo) AS item_name
            partition_key   : Column name that uniquely identifies the product
            date_key        : Column name from which the acquisition date can be determined (must be "date" type)
            price_key       : Column name where price is stored
            old_price_col_name : Specify the column name where the old price will be stored (returned in the result set)
            target_date     : Acquisition reference date (exam:'2024-10-10' -> you can get previous price at '2024-10-09' in same record)
    """
```

If you have your own bigQuery environment for test.
You can specify the environment in the constructor　argument.
Below is an example of how to use the library.

```
"""
 Constructor
"""
# Automatically authenticate here in the Raksul environment
pq = bq_manager.pricing_query()　

# If you want to try it in your own environment, you can pass the authentication information.
cert = {"type": "service_account",
        "project_id": "raksulcrm-dev",
        "private_key_id": "xxxxxxxxxxxxxxxxxxxf948f9f12",
        "private_key": "Omitted below..."}
pq = bq_manager.pricing_query(cert)

"""
 Example of registering data to BigQuery
"""
	rec = json.loads("""
		{"col1":"value1","col3":"value2", "col3","Omitted below..."}
	""")
	records.append(rec)

	bq_full_name = pq.get_qualified_fullname("TableName")
	pq.persist_from_jsonlist(bq_full_name, records)

"""
　Example of checking price changes
"""
rows = pq.get_day_diff(
        target_name=bq_full_name, 
        concat_cols="CONCAT(shape, '-' , unit, '-', eigyo) AS item_name",
        partition_key="s_id", 
        date_key="crawl_date", 
        price_key="price", 
        old_price_col_name="prev_price", 
        target_date="2024-06-05")
        
messages:list = []
for r in rows:
    prev_price = 0 if r.get("prev_price") == None else r.get("prev_price")
    if r.get("price") != prev_price:
        messages.append(f"{r.get("item_name")} : {prev_price} -> {r.get("price")}")
```
