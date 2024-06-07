import json
import requests
import urllib
import boto3
import datetime

POST_URL:str = "https://www.printpac.co.jp/contents/lineup/seal/ajax/get_price.php"

# 商品ID
PRODUCT_PRM_NAME = "category_id"
PRODUCT_ID = 47

# 形とサイズ - 全て取る or 必要なものを確認する
SHAPE_AND_SIZE_PRM_NAME:str = "size_id"
SHAPE_AND_SIZE:dict = {
    600 : "正方形60x60" ,
    601 : "正方形50x50" ,
}

# 印刷用紙 - 全て取る or 必要なものを確認する
PRINT_PAPER_PRM_NAME:str="paper_arr[]"
PRINT_PAPAER:dict = {
    159: "クラフト",
    154: "ミラーコート",
}

# 加工 - 多分パターンがないのですべて取ることになる
PROCESS_PRM_NAME:str="kakou"
PROCESS:dict = {
    1 : "印刷のみ",
    2 : "光沢グロスラミネート",
}

# 税込表記 - どちらが良いか確認する
TAX_PRM_NAME:str = "tax_flag"
TAX_PRM_VALUE:str = "true"

#TODO: 組み合わせによっては色ありの場合もあるので、その場合はどうするか検討する

def doCrawl(s3_bucketname:str, s3_subdir:str)->bool:
    """ 
    この関数I/Fを必ず実装してください。
        
        parameters
            s3_bucketname:str   - 保存先のS3バケット名
            s3_subdir:str       - 保存先のS3サブディレクトリ（末尾/付）
        
        returns
            bool - 成否（エラー時のログ出力は一定充足させてください）
            
        descriptions
            - 対象の商品データを取得してS3に保存するところまで実装してください
            - ファイル名は当該モジュール名+_で開始して末尾にTimestampなどを付与してください
                （関数名が[ppc_seal_teikei.py]なら[ppc_seal_teikei_20220102112233.json]など）
            - ファイルの内容は特に規定はありません。セットで作成するRegisterで解読してください 
    """
    raw_data:dict = __get_price()
    s3_output_data = __convert_for_bigquery(raw_data)
    __put_s3(s3_output_data, s3_bucketname, s3_subdir)
    return True;


def __get_price() -> dict:
    """
        実際に価格表は取れるロジックだが、ここは実装は結構適当なのであくまで一例として。
        Printpacで取得できるRAWデータに必要な属性のみ足し込んでいったん結果を返している
    """
    post_data = {}
    for shape_size in SHAPE_AND_SIZE:
        for paper in PRINT_PAPAER:
            for process in PROCESS:
                post_data = {
                    PRODUCT_PRM_NAME: PRODUCT_ID,
                    SHAPE_AND_SIZE_PRM_NAME: shape_size,
                    PRINT_PAPER_PRM_NAME: paper,
                    PROCESS_PRM_NAME: process,
                    TAX_PRM_NAME: TAX_PRM_VALUE
                }
                
                # POST
                post_data = urllib.parse.urlencode(post_data)
                r = requests.post(
                    POST_URL, 
                    data=post_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"})
                    
                if r.status_code != 200:
                    #FIXME: 存在しない組み合わせがあるのでここはうまく回避した方が良い
                    raise Exception("Error at post. Status Code is " + str(r.status_code))
                    
                res_data = r.json()["tbody"]["body"]
                
                for unit in res_data:
                    #NOTE: リファレンス実装用途なんでデータを抑制します
                    #if int(unit) > 300: continue
                    for eigyo in res_data[unit]:
                        res_data[unit][eigyo]["SHAPE"] = SHAPE_AND_SIZE[shape_size]  
                        res_data[unit][eigyo]["PRINT"] = PRINT_PAPAER[paper]  
                        res_data[unit][eigyo]["KAKOU"] = PROCESS[process]  
                        res_data[unit][eigyo]["UNIT"] = unit
                        res_data[unit][eigyo]["eigyo"] = eigyo
    
    return res_data


def __put_s3(output_data:dict, bucket:str, subdir:str):
    """
        wrapするほどのものでもないのでCrawler側で実装すれば良い
    """
    s3 = boto3.client('s3')
    key = subdir + "printpack-seal-teikei_" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.json'
    res = s3.put_object(Body=json.dumps(output_data, ensure_ascii=False).encode('utf-8'), Bucket=bucket, Key=key)

def __convert_for_bigquery(raw_data:dict) -> dict:
    """
        CrawlerとRegisterの枠組みではどちらがどこまで変換するかなどは開発者が決めてよい
        Register側で変更しても良いが、今回はCrawler側で直接のテーブルスキーマにデータを合わせる。
        実際のテーブルスキーマはBizサイドの方に確認してください。
    """
    # 実際にSeal案件で提示されたスキーマ（ちょっと従来と違ったが）に変換
    SCHEMA_SEAL:dict = {
        "yid":    0,
        "oid1":   0,
        "oid2":   0,
        "oid3":   0,
        "oid4":   0,
        "shape": "",
        "size":  "",
        "color":  0,
        "path":   0,
        "is_variable": False,
        "pid":    0,
        "weight": 0,
        "day":    0,
        "set":    0,
        "List_price":     0,
        "campaign_price": 0,
        "Actual_price":   0,
        "start_date"  : "1999-12-31",
        "end_date"    : "2300-12-31",
        "create_at"   : "1999-12-31",
        "org_spec_id" : ""
    }
    
    records:dict = {}
    index:int = 0
    s_date = datetime.date.today().strftime('%Y-%m-%d')
    for unit in raw_data:
        for eigyo in raw_data[unit]:
            r:dict = SCHEMA_SEAL
            r["yid"] = 21                   # 固定シール
            r["oid1"] = 1                   # 実際は取得元URLにより定型:1, 変形ステッカー:2など 
            r["oid2"] = 80                  # 実際は取得元により定型:80, 自由:83など
            r["oid3"] = 1                   # 糊の種類
            r["oid4"] = 1                   # 1固定（未使用） 
            r["shape"] = raw_data[unit][eigyo]["SHAPE"]             # PPACではサイズとシェイプはone-Stringだが実際は分割して判定して値を入れる
            r["size"] =  raw_data[unit][eigyo]["SHAPE"]             # 同上
            r["color"] = 40                 # 白番ありは50, それ以外は40
            r["path"] = 1                   # 本数、よくわからない
            r["is_variable"] = True         # 変形有無（URLで判断できる）
            r["pid"] = 99                   # むずくは無いがダルい。対応表を定義して設定 
            r["weight"] = 0                 # 0固定 
            r["day"] = int(eigyo)           # 納期
            r["set"] = int(unit)            # 枚数
            r["List_price"] = raw_data[unit][eigyo]["price"]        # priceとprice2があり多分、どっちかがキャンペーン価格 
            r["campaign_price"] = raw_data[unit][eigyo]["price"]    # いったんサンプルでは両方同じ値を入れる
            r["Actual_price"] = raw_data[unit][eigyo]["price"]      # キャンペーンがあればその価格、そうでなければ通常価格、つまり実売価格を
            r["start_date"] = s_date                                # 販売開始価格（最初のクロールした日かな）
            r["end_date"] = "2300-12-31"                            # 遠い未来ならなんでもいい 
            r["create_at"] = s_date                                 # 作成日 
            r["org_spec_id"] = raw_data[unit][eigyo]["s_id"]        # Original ID？　見切れてないので信用しないで確認すること

            #NOTE: 商品仕様単位で一意のKeyはあると価格差分の取得が超楽になるので
            #      S_IDの調査に自信なければyid〜sizeを結合して規格単位で一意にしたものを設定した方が良い
            index += 1            
            records[index] = r.copy()

    return records