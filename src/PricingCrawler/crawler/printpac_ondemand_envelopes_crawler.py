import time
import datetime
import math
import json
import requests
from typing import Any, Dict, List, Union
from requests import Response
from bs4 import BeautifulSoup, Tag, ResultSet
from aws.s3 import S3_Client

from data_convert.convert_bigquery_format import (
    convert_ondemand_envelope_price_for_bigquery,
)

# from shared.constants import ProductCategory
from shared.interfaces import (
    OptionInfo,
    MultiStickerCombination,
    MultiStickerPrice,
    MultiStickerRequestPayload,
    OndemandEnvelopeRequestPayload,
    OndemandEnvelopeCombination
)
from .utils import extract_id, get_webpage, get_first_value_by_attr


"""
    SECTION START
    - すべてのマッピングは、以下のウェブサイトのスクリプトから取得されます。
    - ロジックの変更を検出するために、時々チェックしてください。
      https://www.printpac.co.jp/contents/lineup/sticker_multi/asset/js/content.js?20240711145139
"""
def _set_category_id(print_color: str) -> str:
    category_id_map: Dict = {"1": {"category_id": "65"}, "2": {"category_id": "249"}}
    return category_id_map[print_color]["category_id"]

""" SECTION ENDED """


"""
    SECTION START
    このURLからオプションを取得する: https://www.printpac.co.jp/contents/lineup/sticker_multi/
"""

# サイズ
def _get_all_sizes(html: BeautifulSoup) -> List[OptionInfo]:
    # [
    # {"id": "63", "name": "size"}, # 長3封筒
    # {"id": "67", "name": "size"}, # 角2封筒
    # ]
    sizes: List[OptionInfo] = []
    elements: ResultSet[Tag] = html.find_all("input", type="radio")
    for input in elements:
        name: str = get_first_value_by_attr(input, "name")
        if name == "size":
            id: str = get_first_value_by_attr(input, "value")
            sizes.append({"id": id, "name": name})
    return sizes

# 用紙の種類
def _get_all_paper_types(html: BeautifulSoup) -> List[OptionInfo]:
    # [
    # {"id": "craft", "name": "paper_type"}, # クラフト
    # {"id": "white_kent", "name": "paper_type"}, # ホワイトケント
    # {"id": "white_kent", "name": "paper_type"}, #プライバシー保護
    # ]
    paperTypes: List[OptionInfo] = []
    elements: ResultSet[Tag] = html.find_all("input", type="radio")
    for input in elements:
        name: str = get_first_value_by_attr(input, "name")
        if name == "paper_type":
            id: str = get_first_value_by_attr(input, "value")
            paperTypes.append({"id": id, "name": name})
    return paperTypes

# 用紙の厚さ
def _get_all_papers(html: BeautifulSoup) -> List[OptionInfo]:
    # [
    # {"id": "204", "name": "paper"}, # クラフト85（封筒郵便枠無）
    # {"id": "203", "name": "paper"}, # クラフト85（封筒郵便枠有）
    # {"id": "351", "name": "paper"}, # ホワイトケント80（封筒郵便枠無）
    # {"id": "350", "name": "paper"}, # ホワイトケント80（封筒郵便枠有）
    # {"id": "352", "name": "paper"}, # ホワイトケント100（封筒郵便枠無）
    # {"id": "223", "name": "paper"}, # プライバシー保護100（封筒郵便枠無）
    # ]
    papers: List[OptionInfo] = []
    elements: ResultSet[Tag] = html.find_all("input", type="radio")
    for input in elements:
        name: str = get_first_value_by_attr(input, "name")
        if name == "paper":
            id: str = get_first_value_by_attr(input, "value")
            papers.append({"id": id, "name": name})
    return papers

# 色数
def _get_all_colors(html: BeautifulSoup) -> List[OptionInfo]:
    colors: List[OptionInfo] = []
    # APIから取得
    colors = [
        {"id": [5, 6], "name": "color"}, # モノクロ（スミ1色）印刷
        {"id": [1, 2, 4], "name": "color"}, # フルカラー印刷
    ]
    return colors

# 納期はリクエストに含まれないため、関数は不要

""" SECTION ENDED """


def _create_all_combinations(
    all_sizes: List[OptionInfo],
    all_colors: List[OptionInfo],
    all_papers: List[OptionInfo],
) -> List[OndemandEnvelopeCombination]:
    combinations: List[OndemandEnvelopeCombination] = []

    for size_id in extract_id(all_sizes):
        for color_ids in extract_id(all_colors):
            for paper_id in extract_id(all_papers):
                item: OndemandEnvelopeCombination = {
                    "size_id": size_id,
                    "color_ids": color_ids,
                    "paper_id": paper_id,
                }
                combinations.append(item)

    return combinations


def _get_price(data: OndemandEnvelopeCombination) -> Response:
    url = "https://www.printpac.co.jp/contents/lineup/ondemand_envelope/ajax/get_price4leaflet.php"
    # url = "https://www.printpac.co.jp/contents/lineup/sticker_multi/ajax/get_price.php"
    headers: Dict[str, str] = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    request_payload: OndemandEnvelopeRequestPayload = {
        "category": "27", # 固定
        "size": data["size_id"],
        "color[]": data["color_ids"],
        "paper": data["paper_id"],
        "kakou1": "102",
        "printing": "2",
        "tax_flag": True,
    }
    response: Response = requests.post(
        url,
        headers=headers,
        data=request_payload,
    )
    if response.ok:
        if response.json()["status"] == "OK":
            # print("response: ",response.json()["tbody"]["body"])
            return response
        else:
            print("response: NG!!!")
            raise
    else:
        print("Request failed with status code:", response.status_code)
        raise

def _crawl_ondemand_envelope_prices(
    s3_client: S3_Client,
    file_name: str,
    save_combinations: bool = False,
    interval_s: float = 0.1,
) -> None:
    url = "https://www.printpac.co.jp/contents/lineup/ondemand_envelope/price.php"
    html: BeautifulSoup = get_webpage(url)

    combinations: List[OndemandEnvelopeCombination] = _create_all_combinations(
        all_sizes=_get_all_sizes(html),
        all_colors=_get_all_colors(html),
        all_papers=_get_all_papers(html),
    )

    if save_combinations == True:
        with open("ondemand_envelope_combination.txt", "w") as file:
            json.dump(combinations, file, indent=4, ensure_ascii=False)

    """
        res_data: {
            [unit] : {
                [eigyo]: Dict[str,Union[str,int]]
            }
        }
    """
    count = 0
    part_number = 1
    chunk_size = 64 * 1024 * 1024  # 64 MB
    parts = []
    idx: List[int] = [0]

    number_of_combinations: int = len(combinations)
    ten_pct: int = math.ceil(number_of_combinations / 10)
    print("[Number of Combinations] ", number_of_combinations)

    upload_stream = s3_client.create_multipart_upload(file_name)
    upload_id = upload_stream["UploadId"]
    print(f"Multipart upload initiated with ID: {upload_id}")

    buffer = "{" # これ何？
    # 1つのリクエストで複数の組み合わせを処理する
    for item in combinations:
        if count == (number_of_combinations - 1):
            print("Progress: 100%")
        elif count % ten_pct == 0:
            print("Progress: {}%".format((count * 10 / ten_pct)))

        try:
            # printpacAPI実行
            r: Response = _get_price(item)
            if r is None:
                print("No data returned")
            else:
                """
                response: {
                    [UNIT]: {
                        [EIGYO]: {
                            "1": { # 色数（ex. 1,2,4）
                                "s_id": "1258875",
                                "price": "1880",
                                "price2": "null",
                            }
                        }
                }
                """
                converted_data = convert_ondemand_envelope_price_for_bigquery(
                    r.json(),
                    idx
                )

                buffer += json.dumps(converted_data)[1:-1]  # ブラケットを外す
                buffer += ","

                if len(buffer.encode("utf-8")) >= chunk_size:
                    data_to_upload = buffer
                    buffer = None
                    buffer = ""
                    part_response: Any = s3_client.upload_part(
                        file_name,
                        part_number,
                        upload_id,
                        data_to_upload,
                    )
                    parts.append(
                        {"PartNumber": part_number, "ETag": part_response["ETag"]}
                    )
                    part_number += 1
                count += 1
                time.sleep(interval_s)
        except Exception as e:
            print("Error when requesting item with info: ", item, e)

    # JSONを最終化
    if buffer:
        if buffer[-1] == "}":
            buffer += "}"
        else:
            buffer = buffer.rstrip(",") + "}"
    part_response: Any = s3_client.upload_part(
        file_name,
        part_number,
        upload_id,
        buffer,
    )
    parts.append({"PartNumber": part_number, "ETag": part_response["ETag"]})
    s3_client.complete_multipart_upload(file_name, upload_id, parts)

    print("Success rate: {}%".format(round(count * 100 / number_of_combinations, 2)))


def doCrawl(s3_bucketname: str, s3_subdir: str) -> bool:
    try:
        # 　ファイルの名：<相手-製品> _ <作成時間>.json
        prefix = "printpac-ondemand-envelope_"
        file_name: str = (
            prefix + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".json"
        )
        s3_client = S3_Client(s3_bucketname, s3_subdir)
        _crawl_ondemand_envelope_prices(s3_client, file_name)
        print(f"Uploaded [{prefix+file_name}] successfully")
        return True
    except Exception as e:
        print("Error - ", e)
        return False
