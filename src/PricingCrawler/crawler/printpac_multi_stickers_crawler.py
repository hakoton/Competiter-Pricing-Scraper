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
    convert_multi_sticker_price_for_bigquery,
)
from shared.constants import Lamination, ProductCategory
from shared.interfaces import (
    OptionInfo,
    MultiStickerCombination,
    MultiStickerPrice,
    MultiStickerRequestPayload,
)
from .utils import extract_id, get_webpage, get_first_value_by_attr


"""
    SECTION START
    - すべてのマッピングは、以下のウェブサイトのスクリプトから取得されます。
    - ロジックの変更を検出するために、時々チェックしてください。
      https://www.printpac.co.jp/contents/lineup/sticker_multi/asset/js/content.js?20240711145139
"""


def _set_kakou_id(processing_opt_id: str, paper_half_cut_id: str) -> Union[str, None]:
    # { [processing_opt_id]: { [halfcut_id]: kakou1_id  } ] }
    mapping = {
        "1": {
            "1": ["114", "115", "116", "117"],
            "2": ["617", "618", "619", "620"],
            "3": ["621", "622", "623"],
            "4": ["624", "625", "626", "627", "628"],
            "5": ["629", "630", "631", "632", "633"],
        },
        "2": {
            "1": ["118", "119", "120", "121"],
            "2": ["634", "635", "636", "637"],
            "3": ["638", "639", "640"],
            "4": ["641", "642", "643", "644", "645"],
            "5": ["646", "647", "648", "649", "650"],
        },
        "3": {
            "1": ["110", "111", "112", "113"],
            "2": ["600", "601", "602", "603"],
            "3": ["604", "605", "606"],
            "4": ["607", "608", "609", "610", "611"],
            "5": ["612", "613", "614", "615", "616"],
        },
    }

    kakou_id: str = str(mapping[processing_opt_id][paper_half_cut_id][0])
    return kakou_id if kakou_id != None else None


def _set_category_id(print_color: str) -> str:
    category_id_map: Dict = {"1": {"category_id": "65"}, "2": {"category_id": "249"}}
    return category_id_map[print_color]["category_id"]


def _filter_process_opts_on_paper_id(
    paper_id: str,
) -> List[OptionInfo]:
    processing_opts_1: OptionInfo = {"id": "1", "name": Lamination.GLOSSY_LAMINATED}
    processing_opts_2: OptionInfo = {"id": "2", "name": Lamination.MATTE_LAMINATED}
    processing_opts_3: OptionInfo = {"id": "3", "name": Lamination.NO_LAMINATION}

    paper_processing_map: Dict[str, List[OptionInfo]] = {
        "404": [  # 塩ビ（マット）
            processing_opts_2,
            processing_opts_3,
        ],
        "409": [  # 塩ビ（ツヤ）lite [用紙の厚さ薄め]
            processing_opts_1,
            processing_opts_3,
        ],
        "405": [  # PET
            processing_opts_1,
            processing_opts_2,
            processing_opts_3,
        ],
        "default": [
            processing_opts_1,
            processing_opts_2,
            processing_opts_3,
        ],
    }
    return paper_processing_map.get(paper_id, paper_processing_map["default"])


def _filter_halfcut_option(
    halfcut_opts: List[OptionInfo], size_id: str
) -> List[OptionInfo]:
    if size_id == "14":  # ハガキサイズ（100×148mm）
        # small size doesn't support halfcut more than 10
        # 4: 11~15本 , 5: 16~20本
        return [e for e in halfcut_opts if e["id"] not in ["4", "5"]]
    else:
        return halfcut_opts


""" SECTION ENDED """


"""
    SECTION START
    このURLからオプションを取得する: https://www.printpac.co.jp/contents/lineup/sticker_multi/
"""


def _get_all_sizes(html: BeautifulSoup) -> List[OptionInfo]:
    # [
    # {"id": "14", "name": "ハガキサイズ（100×148mm）"},
    # {"id": "4", "name": "A4サイズ（210×297mm）"},
    # ]
    sizes: List[OptionInfo] = []
    elements: ResultSet[Tag] = html.find_all("input", type="radio")
    for input in elements:
        name: str = get_first_value_by_attr(input, "name")
        if name == "size":
            id: str = get_first_value_by_attr(input, "value")
            sizes.append({"id": id, "name": name})

    return sizes


# kami_mei_id
def _get_print_colors(html: BeautifulSoup) -> List[OptionInfo]:
    # CMYK印刷 | RGB+α印刷
    print_colors: List[OptionInfo] = []
    elements: ResultSet[Tag] = html.find_all("input", type="radio")
    for input in elements:
        name: str = get_first_value_by_attr(input, "name")
        if name == "print_color":
            id: str = get_first_value_by_attr(input, "value")
            print_colors.append({"id": id, "name": name})

    return print_colors


def _get_all_papers(html) -> List[OptionInfo]:
    papers: List[OptionInfo] = []
    elements: ResultSet[Tag] = html.find_all("input", type="radio")
    for input in elements:
        name: str = get_first_value_by_attr(input, "name")
        if name == "paper":
            id: str = get_first_value_by_attr(input, "value")

            papers.append({"id": id, "name": name})

    return papers


def _get_halfcut_amount(html) -> List[OptionInfo]:
    half_cut_amount: List[OptionInfo] = []
    elements: ResultSet[Tag] = html.find_all("input", type="radio")
    for input in elements:
        name: str = get_first_value_by_attr(input, "name")
        if name == "halfcat":
            id: str = get_first_value_by_attr(input, "value")
            half_cut_amount.append({"id": id, "name": name})

    return half_cut_amount


""" SECTION ENDED """


def _create_all_combinations(
    all_sizes: List[OptionInfo],
    print_colors: List[OptionInfo],
    papers: List[OptionInfo],
    halfcut_options: List[OptionInfo],
) -> List[MultiStickerCombination]:
    combinations: List[MultiStickerCombination] = []

    for size_id in extract_id(all_sizes):
        for color_id in extract_id(print_colors):
            for paper_id in extract_id(papers):
                process_opts: List[OptionInfo] = _filter_process_opts_on_paper_id(
                    paper_id
                )
                for process_opt in process_opts:
                    for halfcut_opt in _filter_halfcut_option(halfcut_options, size_id):
                        item: MultiStickerCombination = {
                            "size_id": size_id,
                            "print_color_id": color_id,
                            "half_cut_amount_id": halfcut_opt["id"],
                            "paper_id": paper_id,
                            "processing_opt_id": process_opt["id"],
                            "processing_opt_name": process_opt["name"],
                        }
                        combinations.append(item)

    return combinations


def _get_price(data: MultiStickerCombination) -> Dict:
    url = "https://www.printpac.co.jp/contents/lineup/sticker_multi/ajax/get_price.php"
    headers: Dict[str, str] = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.printpac.co.jp",
        "Referer": "https://www.printpac.co.jp/contents/lineup/sticker_multi/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    request_payload: MultiStickerRequestPayload = {
        "c_id": _set_category_id(data["print_color_id"]),
        "irokazu_id": "1",  # 固定
        "houhou_id": "2",  # 固定
        "size_id": data["size_id"],
        "kami_mei_id": data["paper_id"],
        "kakou1_id": _set_kakou_id(
            data["processing_opt_id"], data["half_cut_amount_id"]
        ),
        "tax_flag": False,
    }
    response: Response = requests.post(
        url,
        headers=headers,
        data=request_payload,
    )
    if response.ok:
        res_data = response.json()
        if "tbody" not in res_data:
            print(f"failed to fetch data: {request_payload} - Error {res_data}")
            raise RuntimeWarning("COMBINATION_NOT_EXIST")
        return res_data

    else:
        print("Request failed with status code:", response.status_code)
        raise


def _crawl_multi_sicker_prices(
    s3_client: S3_Client,
    file_name: str,
    save_combinations: bool = False,
    interval_s: float = 0.1,
) -> None:
    url = "https://www.printpac.co.jp/contents/lineup/sticker_multi/"
    html: BeautifulSoup = get_webpage(url)

    combinations: List[MultiStickerCombination] = _create_all_combinations(
        all_sizes=_get_all_sizes(html),
        halfcut_options=_get_halfcut_amount(html),
        papers=_get_all_papers(html),
        print_colors=_get_print_colors(html),
    )

    if save_combinations == True:
        with open("/tmp/multi_sticker_combination.txt", "w") as file:
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

    buffer = "{"
    for item in combinations:
        if count == (number_of_combinations - 1):
            print("Progress: 100%")
        elif count % ten_pct == 0:
            print("Progress: {}%".format((count * 10 / ten_pct)))

        try:
            r: Dict = _get_price(item)
            if r is None:
                print("No data returned")
            else:
                """
                response: {
                    [UNIT]: {
                        [EIGYO]: {
                            "1": { # "1" 固定
                                "s_id": "44246959",
                                "t_id": "797287",
                                "price": "1110",
                                "price2": "1420",
                                "tax": 101,
                                "tax2": 129
                            }
                        }
                }
                """
                res_data = r["tbody"]["body"]

                for unit in res_data:
                    for eigyo in res_data[unit]:
                        # TODO:　なぜ”１”が存在する
                        price: MultiStickerPrice = res_data[unit][eigyo]["1"]
                        price["KAKOU"] = item["processing_opt_id"]
                        price["KAKOU_NAME"] = item["processing_opt_name"]  # Lamination
                        price["UNIT"] = unit
                        price["SHAPE"] = "multi"
                        price["SIZE_ID"] = item["size_id"]
                        price["PAPER_ID"] = item["paper_id"]
                        price["HALF_CUT"] = item["half_cut_amount_id"]
                        price["COLOR_ID"] = item["print_color_id"]
                        price["eigyo"] = eigyo
                        # Override "1" object with information
                        res_data[unit][eigyo] = price

                converted_data = convert_multi_sticker_price_for_bigquery(
                    ProductCategory.SEAL, res_data, idx
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
        prefix = "printpac-multi-sticker_"
        file_name: str = (
            prefix + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".json"
        )
        s3_client = S3_Client(s3_bucketname, s3_subdir)
        _crawl_multi_sicker_prices(s3_client, file_name)
        print(f"Uploaded [{file_name}] successfully")
        return True
    except Exception as e:
        print("Error - ", e)
        return False
