import time
import datetime
import math
import json
import requests
from typing import Dict, List
from requests import Response
from bs4 import BeautifulSoup, Tag, ResultSet
from aws.s3 import put_s3

from data_convert.convert_bigquery_format import convert_sticker_price_for_bigquery
from shared.constants import STICKER_SIZE_TABLE, ProductCategory
from shared.interfaces import (
    OptionInfo,
    StickerSizeInfo,
    StickerCombination,
    StickerPrice,
    StickerRequestPayload,
)
from .utils import get_webpage, get_first_value_by_attr


def _extract_id(data: List[OptionInfo]) -> List[str]:
    return [e["id"] for e in data]


"""
    SECTION START
    - すべてのマッピングは、以下のウェブサイトのスクリプトから取得されます。
    - ロジックの変更を検出するために、時々チェックしてください。
      https://www.printpac.co.jp/contents/lineup/sticker/js/content.js?20240706130210
"""


def _set_kakou_id(processing_opt_id: str, paper_half_cut_id: str) -> str:
    # { [paper_processing_opt_id]: { [paper_half_cut_id]: kakou_id  } ] }
    mapping = {
        "1": {
            "1": {"kakou_id": "114"},
            "2": {"kakou_id": "115"},
            "3": {"kakou_id": "116"},
            "4": {"kakou_id": "117"},
        },
        "2": {
            "1": {"kakou_id": "118"},
            "2": {"kakou_id": "119"},
            "3": {"kakou_id": "120"},
            "4": {"kakou_id": "121"},
        },
        "3": {
            "1": {"kakou_id": "125"},
            "2": {"kakou_id": "126"},
            "3": {"kakou_id": "127"},
            "4": {"kakou_id": "128"},
        },
        "4": {
            "1": {"kakou_id": "110"},
            "2": {"kakou_id": "111"},
            "3": {"kakou_id": "112"},
            "4": {"kakou_id": "113"},
        },
    }
    kakou_id: str = mapping[processing_opt_id][paper_half_cut_id]["kakou_id"]
    return kakou_id if kakou_id != None else "0"


def _set_category_id(print_color: str) -> str:
    category_id_map: Dict = {"1": {"category_id": "28"}, "2": {"category_id": "248"}}
    return category_id_map[print_color]["category_id"]


def _set_paper_id(material_id: str) -> str:
    # paper_material_id -> kami_mei_id
    mapping: Dict[str, str] = {
        "1": "402",
        "2": "405",
        "3": "403",
        "4": "404",
        "5": "409",
        "6": "400",
        "default": "0",
    }
    return mapping.get(material_id, mapping["default"])


def _filter_process_opts_on_paper_material(
    material_id: str,
) -> List[OptionInfo]:
    processing_opts_1: OptionInfo = {"id": "1", "name": "つや ラミネート"}
    processing_opts_2: OptionInfo = {"id": "2", "name": "マット ラミネート"}
    processing_opts_3: OptionInfo = {"id": "3", "name": "エンボス ラミネート"}
    processing_opts_4: OptionInfo = {"id": "4", "name": "ラミネートなし"}

    # { [material_id]: List[process_opt] }
    paper_processing_map: Dict[str, List[OptionInfo]] = {
        "3": [
            processing_opts_1,
            processing_opts_4,
        ],
        "5": [
            processing_opts_1,
            processing_opts_4,
        ],
        "4": [
            processing_opts_2,
            processing_opts_4,
        ],
        "6": [
            processing_opts_3,
            processing_opts_4,
        ],
        "default": [
            processing_opts_1,
            processing_opts_2,
            processing_opts_4,
        ],
    }
    return paper_processing_map.get(material_id, paper_processing_map["default"])


""" SECTION ENDED """

"""
    SECTION START
    このURLからオプションを取得する: https://www.printpac.co.jp/contents/lineup/sticker/
"""


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


def _get_all_materials(html: BeautifulSoup) -> List[OptionInfo]:
    materials: List[OptionInfo] = []
    elements: ResultSet[Tag] = html.find_all("input", type="radio")
    for input in elements:
        name: str = get_first_value_by_attr(input, "name")
        if name == "paper_material":
            id: str = get_first_value_by_attr(input, "value")
            materials.append({"id": id, "name": name})

    return materials


def _get_halfcut_amount(html: BeautifulSoup) -> List[OptionInfo]:
    half_cut_amount: List[OptionInfo] = []
    elements: ResultSet[Tag] = html.find_all("input", type="radio")
    for input in elements:
        name: str = get_first_value_by_attr(input, "name")
        if name == "paper_halfcut":
            id: str = get_first_value_by_attr(input, "value")
            half_cut_amount.append({"id": id, "name": name})

    return half_cut_amount


""" SECTION ENDED """


def _create_all_combinations(
    all_sizes: Dict[str, StickerSizeInfo],
    print_colors: List[OptionInfo],
    materials: List[OptionInfo],
    half_cut_amount: List[OptionInfo],
) -> List[StickerCombination]:
    combinations: List[StickerCombination] = []
    for size in all_sizes:
        for color_id in _extract_id(print_colors):
            for material_id in _extract_id(materials):
                process_opts: List[OptionInfo] = _filter_process_opts_on_paper_material(
                    material_id
                )
                for process_opt in process_opts:
                    for cut_amount_id in _extract_id(half_cut_amount):
                        item: StickerCombination = {
                            "size_id": all_sizes[size]["size_id"],
                            "size_range": size,
                            "width": all_sizes[size]["size_sample"]["width"],
                            "height": all_sizes[size]["size_sample"]["height"],
                            "half_cut_amount_id": cut_amount_id,
                            "material_id": material_id,
                            "print_color_id": color_id,
                            "processing_opt_id": process_opt["id"],
                            "processing_opt_name": process_opt["name"],
                        }
                        combinations.append(item)

    return combinations


def _get_price(data: StickerCombination) -> Response:
    url = "https://www.printpac.co.jp/contents/lineup/sticker/ajax/get_price.php"
    headers: Dict[str, str] = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    request_payload: StickerRequestPayload = {
        "c_id": _set_category_id(data["print_color_id"]),
        "fix_size_w": data["width"],
        "fix_size_h": data["height"],
        "size": data["size_id"],
        "kakou1": _set_kakou_id(data["processing_opt_id"], data["half_cut_amount_id"]),
        "kami_mei": _set_paper_id(data["material_id"]),
        "houhou": "2",  # 固定
        "irokazu": "1",  # 固定
        "tax_flag": False,
    }
    response: Response = requests.post(
        url,
        headers=headers,
        data=request_payload,
    )
    if response.ok:
        return response

    else:
        print("Request failed with status code:", response.status_code)
        raise


def _crawl_sicker_prices(
    save_combinations: bool = False,
    save_prices: bool = False,
    interval_s: float = 0.1,
) -> Dict[str, Dict[str, StickerPrice]]:
    url = "https://www.printpac.co.jp/contents/lineup/sticker/"
    html: BeautifulSoup = get_webpage(url)

    combinations: List[StickerCombination] = _create_all_combinations(
        all_sizes=STICKER_SIZE_TABLE,
        half_cut_amount=_get_halfcut_amount(html),
        materials=_get_all_materials(html),
        print_colors=_get_print_colors(html),
    )

    if save_combinations == True:
        with open("sticker_combination.txt", "w") as file:
            json.dump(combinations, file, indent=4, ensure_ascii=False)

    """
        res_data: {
            [unit] : {
                [eigyo]: Dict[str,Union[str,int]]
            }
        }
    """
    count: int = 0
    idx: List[int] = [0]
    result: Dict[str, Dict[str, StickerPrice]] = {}

    number_of_combinations: int = len(combinations)
    ten_pct: int = math.ceil(number_of_combinations / 10)
    print("[Number of Combinations] ", number_of_combinations)

    for item in combinations:
        if count == (number_of_combinations - 1):
            print("Progress: 100%")
        elif count % ten_pct == 0:
            print("Progress: {}%".format((count * 10 / ten_pct)))

        try:
            r: Response = _get_price(item)
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
                res_data = r.json()["tbody"]["body"]

                for unit in res_data:
                    for eigyo in res_data[unit]:
                        # TODO:　なぜ”１”が存在する
                        price: StickerPrice = res_data[unit][eigyo]["1"]
                        price["KAKOU"] = item["processing_opt_id"]
                        price["KAKOU_NAME"] = item["processing_opt_name"]
                        price["UNIT"] = unit
                        price["SHAPE"] = "自由"
                        price["SIZE_RANGE"] = item["size_range"]
                        price["MATERIAL_ID"] = item["material_id"]
                        price["HALF_CUT"] = item["half_cut_amount_id"]
                        price["COLOR_ID"] = item["print_color_id"]
                        price["eigyo"] = eigyo
                        # Override "1" object with information
                        res_data[unit][eigyo] = price
                result.update(
                    convert_sticker_price_for_bigquery(
                        ProductCategory.STICKER, res_data, idx
                    )
                )
                count += 1
                time.sleep(interval_s)
        except Exception as e:
            print("Error when requesting item with info: ", item, e)

    if save_prices == True:
        with open("sticker_prices.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    print("Success rate: {}%".format(round(count * 100 / number_of_combinations, 2)))
    return result


def doCrawl(s3_bucketname: str, s3_subdir: str) -> bool:
    try:
        converted_data: Dict[str, Dict[str, StickerPrice]] = _crawl_sicker_prices()

        # 　ファイルの名：<相手-製品> _ <作成時間>.json
        prefix = "printpac-sticker_"
        key: str = (
            s3_subdir
            + prefix
            + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            + ".json"
        )
        with open(
            prefix + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".json",
            "w",
        ) as file:
            json.dump(converted_data, file, indent=4, ensure_ascii=False)
        print(f"Uploading [{key}] ...")
        put_s3(converted_data, s3_bucketname, key)
        print(f"Uploaded [{key}] successfully")
        return True
    except Exception as e:
        print("Error - ", e)
        return False
