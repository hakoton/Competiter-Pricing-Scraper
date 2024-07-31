# -*- coding: utf-8 -*-
import datetime
import math
import requests
from requests import Response
import json
from typing import List, Union, Dict
from bs4 import BeautifulSoup, NavigableString, Tag, ResultSet
import time

from shared.constants import SEAL_PID_TABLE, Lamination
from shared.interfaces import (
    LabelSealRequestPayload,
    OptionInfo,
    SealCombination,
    SealPrice,
)
from aws.s3 import put_s3
from data_convert.convert_bigquery_format import (
    ProductCategory,
    convert_seal_price_for_bigquery,
)
from .utils import get_webpage, get_first_value_by_attr  # 用紙の種類

tax_flag: str = "false"


"""
    SECTION START
    - すべてのマッピングは、以下のウェブサイトのスクリプトから取得されます。
    - ロジックの変更を検出するために、時々チェックしてください。
      https://www.printpac.co.jp/contents/lineup/seal/js/size.js?20240612164729
"""
laminate_group: List[int] = [1, 2, 3, 4, 6, 7, 8]
whitesheet_group: List[int] = [11, 14, 15, 19]
whitesheet_laminate_group: List[int] = [8]

SealProcessId: Dict[Lamination, int] = {
    Lamination.NO_LAMINATION: 1,
    Lamination.GLOSSY_LAMINATED_PP: 2,
    Lamination.MATTE_LAMINATED_PP: 3,
    Lamination.WHITE_PLATE: 4,
    Lamination.GLOSSY_LAMINATED_PP_WITH_WHITE_PLATE: 5,
    Lamination.MATTE_LAMINATED_PP_WITH_WHITE_PLATE: 6,
}


def _in_laminate_group(paper_group_id: str) -> bool:
    if int(paper_group_id) not in laminate_group:
        return False
    else:
        return True


def _in_whitesheet_group(paper_group_id: str) -> bool:
    if int(paper_group_id) not in whitesheet_group:
        return False
    else:
        return True


def _in_whitesheet_laminate_group(paper_group_id: str) -> bool:
    if int(paper_group_id) not in whitesheet_laminate_group:
        return False
    else:
        return True


def _filter_pp_process_options_by_print_paper(paper_group_id: str) -> List[int]:
    """
    加工のオプション
    デフォルトオプション: ラミネートなし
    """
    process_options: List[int] = [SealProcessId[Lamination.NO_LAMINATION]]

    if _in_laminate_group(paper_group_id):
        process_options.append(SealProcessId[Lamination.GLOSSY_LAMINATED_PP])  # 2
        process_options.append(SealProcessId[Lamination.MATTE_LAMINATED_PP])  # 3
    if _in_whitesheet_group(paper_group_id):
        process_options.append(SealProcessId[Lamination.WHITE_PLATE])  # 4
    if _in_whitesheet_laminate_group(paper_group_id):
        process_options.append(
            SealProcessId[Lamination.GLOSSY_LAMINATED_PP_WITH_WHITE_PLATE]
        )  # 5
    return process_options


def _set_category_id(paper_process: int) -> int:
    # [2,3]
    if paper_process in [
        SealProcessId[Lamination.GLOSSY_LAMINATED_PP],
        SealProcessId[Lamination.MATTE_LAMINATED_PP],
    ]:
        category_id = 59
    # [4, 5, 6]
    elif paper_process in [
        SealProcessId[Lamination.WHITE_PLATE],
        SealProcessId[Lamination.GLOSSY_LAMINATED_PP_WITH_WHITE_PLATE],
        SealProcessId[Lamination.MATTE_LAMINATED_PP_WITH_WHITE_PLATE],
    ]:
        category_id = 91
    else:
        category_id = 47

    return category_id


def _set_paper_id_arr(paper_group_id: str) -> Union[List[int], None]:
    return [e for e in SEAL_PID_TABLE[int(paper_group_id)]]


""" SECTION ENDED """


"""
    SECTION START
    このURLからオプションを取得する:: https://www.printpac.co.jp/contents/lineup/seal/size.php
"""


def _get_all_sizes(html: BeautifulSoup) -> List[OptionInfo]:
    """
    HTMLからすべての用紙サイズ要素をフィルタリングして返す
    """
    size_divs: ResultSet[Tag] = html.find_all(class_="size")

    """
    サイズ要素のリストを処理し、サイズ辞書のリストを返す
    結果の例: [{'size': 'Square 60mm×60mm', 'size_id': '600'}]
    """
    result: List[OptionInfo] = []
    for div in size_divs:
        # size_name を抽出
        size_name: str = get_first_value_by_attr(div, "alt")

        # size_id を抽出
        size_id: str = ""
        size_element: Union[Tag, NavigableString, None] = div.find("input")
        if isinstance(size_element, Tag):
            value: Union[str, list[str]] = size_element["value"]
            if isinstance(value, str):
                size_id = value
            else:
                size_id = value[0]
        else:
            raise ValueError("size_element is not a Tag")

        result.append({"name": size_name, "id": size_id})

    return result


def _get_all_print_papers(html: BeautifulSoup) -> List[OptionInfo]:
    """
    HTMLからすべての印刷用紙オプションを抽出
    2つの主要なグループ:
    グループ1: カス上げなし
    グループ2: カス上げあり
    結果の例: [{'paper_name': '', 'paper_group_id': ''}]
    """
    result: List[OptionInfo] = []

    groups: ResultSet[Tag] = html.find_all(class_="paper_group")
    if len(groups) == 0:
        raise ValueError("groups does not have any elements")

    list_items: List[Tag] = []
    for group in groups:
        li: ResultSet[Tag] = group.find_all("li")
        list_items.extend(li)

    # リストの項目をループ処理
    for item in list_items:
        input_element: Union[Tag, NavigableString, None] = item.find("input")

        if isinstance(input_element, Tag):
            paper_name: str = get_first_value_by_attr(input_element, "data-name")
            paper_group_id: str = get_first_value_by_attr(input_element, "value")
            result.append({"name": paper_name, "id": paper_group_id})

    return result


def _get_all_paper_process_options(html: BeautifulSoup) -> Dict[str, str]:
    """
    {
        [key: paper_process_option_id]: paper_process_option_name
    }
    結果の例:
    {
        '1': 'ラミネートなし',
        '2': '光沢グロスPPラミネート',
        '3': 'マットPPラミネート',
        '4': '白版追加',
        '5': '光沢グロスPPラミネート＋白版追加',
        '6': 'マットPPラミネート＋白版追加'
    }
    """
    paper_process_el = html.find_all("input", {"name": "kakou"})
    obj = {}
    for el in paper_process_el:
        obj[el["value"]] = el["data-name"]

    return obj


""" SECTION ENDED """


def _get_price(data) -> Response:
    url = "https://www.printpac.co.jp/contents/lineup/seal/ajax/get_price.php"
    headers: Dict[str, str] = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    request_payload: LabelSealRequestPayload = {
        "category_id": data["category_id"],
        "size_id": data["size_id"],
        "paper_arr[]": data["paper_arr"],
        "kakou": data["kakou"],
        "tax_flag": data["tax_flag"],
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


def _create_all_combinations(
    sizes: List[OptionInfo],
    print_papers: List[OptionInfo],
    paper_process_option: Dict[str, str],
) -> List[SealCombination]:
    combinations: List[SealCombination] = []
    for size in sizes:
        for print_pp in print_papers:
            possible_paper_process: List[int] = (
                _filter_pp_process_options_by_print_paper(print_pp["id"])
            )
            for process in possible_paper_process:
                # 一部の印刷用紙には異なるカスタマイズオプションがある
                paper_id_arr = _set_paper_id_arr(print_pp["id"])
                if paper_id_arr is None:
                    continue
                else:
                    for paper_id in paper_id_arr:
                        obj: SealCombination = {
                            "category_id": str(_set_category_id(process)),
                            "size_id": size["id"],
                            "paper_arr": str(paper_id),  # paper id
                            "kakou": str(process),
                            "tax_flag": tax_flag,
                            # クエリに必要な情報以外の詳細
                            "paper_name": print_pp["name"],
                            "paper_group_id": print_pp["id"],
                            "shape": size["name"],
                            "process": paper_process_option.get(str(process), "1"),
                        }
                        combinations.append(obj)

    return combinations


def _crawl_label_seal_prices(
    save_combinations: bool = False,
    interval_s: float = 0.1,
) -> Dict[str, Dict[str, SealPrice]]:
    """
    ラベルとステッカーの価格をクロール
    save_combinations: すべての組み合わせをローカルファイルに保存するかどうか
    interval_s:       各リクエスト間の間隔
    """
    url = "https://www.printpac.co.jp/contents/lineup/seal/size.php"
    html: BeautifulSoup = get_webpage(url)

    # 1. すべてのサイズを取得（サイズは定数）
    sizes: List[OptionInfo] = _get_all_sizes(html)

    # 2. 印刷用紙（シールの紙質）を取得
    print_papers: List[OptionInfo] = _get_all_print_papers(html)
    paper_process_option: Dict[str, str] = _get_all_paper_process_options(html)
    combinations: List[SealCombination] = _create_all_combinations(
        sizes, print_papers, paper_process_option
    )

    if save_combinations == True:
        with open("seal_combination.txt", "w") as file:
            json.dump(combinations, file, indent=4, ensure_ascii=False)

    """
        res_data: {
            [unit] : {
                [eigyo]: Dict[str,Union[str,int]]
            }
        }
    """
    count = 0
    idx: List[int] = [0]
    result: Dict[str, Dict[str, SealPrice]] = {}

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
                res_data: Dict[str, Dict[str, SealPrice]] = r.json()["tbody"]["body"]

                for unit in res_data:
                    for eigyo in res_data[unit]:
                        res_data[unit][eigyo]["SHAPE"] = item["shape"]
                        res_data[unit][eigyo]["PRINT"] = item["paper_name"]
                        res_data[unit][eigyo]["KAKOU"] = item["process"]
                        res_data[unit][eigyo]["PAPER_GROUP_ID"] = item["paper_group_id"]
                        res_data[unit][eigyo]["PAPER_ID"] = item["paper_arr"]

                        res_data[unit][eigyo]["UNIT"] = unit
                        res_data[unit][eigyo]["eigyo"] = eigyo

                result.update(
                    convert_seal_price_for_bigquery(ProductCategory.SEAL, res_data, idx)
                )
                count += 1
                time.sleep(interval_s)
        except Exception as e:
            print("Error when requesting item with info: ", item, e)

    print("Success rate: {}%".format(round(count * 100 / number_of_combinations, 2)))
    return result


def doCrawl(s3_bucketname: str, s3_subdir: str) -> bool:
    try:
        converted_data: Dict[str, Dict[str, SealPrice]] = _crawl_label_seal_prices()

        # 　ファイルの名：<相手-製品> _ <作成時間>.json
        prefix = "printpac-label-seal_"
        key: str = (
            s3_subdir
            + prefix
            + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            + ".json"
        )
        print(f"Uploading [{key}] ...")
        put_s3(converted_data, s3_bucketname, key)
        print(f"Uploaded [{key}] successfully")
        return True
    except Exception as e:
        print("Error - ", e)
        return False
