"""
こちらはサンプルモジュールです。
実装の流れのみ参考にして、詳細仕様はBizオーナーと確認して実装をお願いします。
"""
import sys
import json
import datetime

# BigQuery操作やSlack通知などで必要なモジュールをImportします
sys.path.append('../')
from lib import bq_manager
from lib import slack

# BiqQuery関係
BQ_TABLE:str = "ppc_seal_price"

def doRegist(data:bytes)->bool:
    """ この関数I/Fを必ず実装してください。
    
        parameters
            data:bytes - CrawlerでS3保存したファイル内容(Byte配列)
    
        returns
            boole - 成否（失敗時のログは一定残してください）
        
        descriptions
            - CrawlしたデータをBigQueryへ投入するところまでを実装してください
            - Crawlerと異なり以下のライブラリを利用する必要があります
            　適宜Mockで実装進めるなり、貴社のSlackやBigquery環境で動作確認してください。
                ⚫️ 一部定数はglobal_settings.py
                ⚫︎ Slack通知はslack_manager.pyを利用
                ⚫︎ BigQuery操作系はbq_manager.pyを利用
    """
  
    # データは以下のように取り出せます（ローカル開発時は直接Readしても如何ようにも）
    # Crawlerと対で認識対応であればS3に配置した中間ファイル形式は不問ですが、Jsonをお勧めします
    data = {} if data == None else json.loads(data.decode("utf-8"))


    """
    実現性確認のためだけのコードで、サンプリングして適当にデータを突っ込んでます
    実際はバルクで効率よく登録するなどしてください。
    """
    records:list = []
    cnt=0
    for unit in data:
        if int(unit) > 500: continue
        for eigyo in data[unit]:
            target = data[unit][eigyo]
            rec = json.loads(
            """{{
                "s_id":"{}",
                "price":"{}",
                "price2":"{}",
                "irokazu_id":"{}",
                "shape":"{}",
                "print":"{}",
                "unit":"{}",
                "kakou":"{}",
                "eigyo":"{}",
                "crawl_date":"{}",
                "crawl_at":"{}"
            }}""".format(
                target["s_id"],
                target["price"],
                0 if target["price2"] == None else target["price2"],
                target["irokazu_id"],
                target["SHAPE"],
                target["PRINT"],
                unit,
                target["KAKOU"],
                eigyo,
                datetime.date.today(),
                datetime.datetime.now()
                ), strict=False)
            records.append(rec)
            cnt+=1
            if cnt > 2: break

    """
    BigQueryでの投入は2024.6時点でJsonからのInsertにのみ対応しています
    スキーマ定義はBizサイドから展開してもらってください
    """
    
    pq = bq_manager.pricing_query()
    bq_full_name:str = pq.get_qualified_fullname(BQ_TABLE)
    # pq.persist_from_jsonlist(bq_full_name, records)
    
    # 差分抽出
    rows = pq.get_day_diff(
            target_name=bq_full_name, 
            concat_cols="CONCAT(shape, '-' , unit, '-', eigyo) AS item_name",
            partition_key="s_id", 
            date_key="crawl_date", 
            price_key="price", 
            old_price_col_name="prev_price", 
            target_date="2024-06-05")
        
    # 単価変更を取得する
    # Note: あんまり多いと大変なので一定で切り捨てるとかしても良いかも
    messages:list = []
    for r in rows:
        prev_price = 0 if r.get("prev_price") == None else r.get("prev_price")
        if r.get("price") != prev_price:
            messages.append(f"{r.get("item_name")} : {prev_price} -> {r.get("price")}")

    # Slackの通知テスト 以下のように通知が可能です。通知内容はBizと会話して決めてください。
    #slack.notify("【テスト】PrintPac:定型シールの価格取得完了 : 107件")
    if len(messages) > 0:
        send_message = "価格変更がありました。\n\n"
        for m in messages:
            send_message += (m + "\n")
        
        #slack.notify(send_message)
        print(send_message)
        
    return True