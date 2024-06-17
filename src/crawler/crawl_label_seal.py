import requests
from requests import Response
import json
from typing import List, Union, Any, Dict
from bs4 import BeautifulSoup, NavigableString, Tag, ResultSet
import time
from utils import get_webpage, get_first_value_by_attr

# 印刷用紙IDと対応する用紙IDのマッピング
paper_id_map: Dict[str, List[int]] = {
    """
    key: print_paper
    value: paper_id
    """
    "1": [152],
    "2": [154],
    "3": [153],
    "4": [157],
    "5": [155],
    "6": [158],
    "7": [156],
    "8": [173],
    "9": [147],
    "10": [148],
    "11": [159],
    "12": [174],
    "13": [435, 419, 432, 433, 434],
    "14": [175, 176, 177, 178, 179],
    "15": [417, 418],
    "16": [194],
    "17": [192],
    "18": [193],
    "19": [415, 416],
    "21": [472],
    "23": [473],
    "24": [471],
    "25": [474],
    "26": [470],
}

# 用紙の種類
laminate_group: List[int] = [1, 2, 3, 4, 6, 7, 8]
whitesheet_group: List[int] = [11, 14, 15, 19]
whitesheet_laminate_group: List[int] = [8]
tax_flag: str = "true"


def get_all_paper_size_el(soup: BeautifulSoup) -> List[Tag]:
    """
    HTMLからすべての用紙サイズ要素をフィルタリングして返す
    """
    elements: ResultSet[Tag] = soup.find_all(class_="size")
    return elements


def extract_all_sizes(size_divs: List[Tag]) -> List[Dict[str, str]]:
    """
    サイズ要素のリストを処理し、サイズ辞書のリストを返す
    結果の例: [{'size': 'Square 60mm×60mm', 'size_id': '600'}]
    """
    result: List[Dict[str, str]] = []
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

        obj: dict[str, str] = {"size": size_name, "size_id": size_id}
        result.append(obj)

    return result


def extract_all_print_papers(html: BeautifulSoup) -> List[Dict[str, str]]:
    """
    HTMLからすべての印刷用紙オプションを抽出
    2つの主要なグループ:
    グループ1: カス上げなし
    グループ2: カス上げあり
    結果の例: [{'print_paper_name': '', 'print_paper_id': ''}]
    """
    result: List[Dict[str, str]] = []

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
            print_paper_name: str = get_first_value_by_attr(input_element, "data-name")
            print_paper_id: str = get_first_value_by_attr(input_element, "value")
            obj: Dict[str, str] = {
                "print_paper_name": print_paper_name,
                "print_paper_id": print_paper_id,
            }
            result.append(obj)

    return result


def has_laminate(print_paper: str) -> bool:
    val: int = int(print_paper)
    if val not in laminate_group:
        return False
    else:
        return True


def has_whitesheet(print_paper: str) -> bool:
    val: int = int(print_paper)
    if val not in whitesheet_group:
        return False
    else:
        return True


def has_whitesheet_laminate(print_paper: str) -> bool:
    val: int = int(print_paper)
    if val not in whitesheet_laminate_group:
        return False
    else:
        return True


def get_paper_process_option(html: BeautifulSoup) -> Dict[str, str]:
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


def filter_paper_process_by_print_paper(print_paper: str) -> List[int]:
    # デフォルトオプション: ラミネートなし
    paper_process: List[int] = [1]

    if has_laminate(print_paper):
        paper_process.append(2)
        paper_process.append(3)
    if has_whitesheet(print_paper):
        paper_process.append(4)
    if has_whitesheet_laminate(print_paper):
        paper_process.append(5)
    return paper_process


def get_paper_id_arr(print_paper: str) -> Union[List[int], None]:
    return paper_id_map.get(print_paper)


def generate_category_id(paper_process: int) -> int:
    if paper_process == 2 or paper_process == 3:
        category_id = 59
    elif paper_process == 4 or paper_process == 5 or paper_process == 6:
        category_id = 91
    else:
        category_id = 47

    return category_id


def get_price(data, count) -> Response:
    url = "https://www.printpac.co.jp/contents/lineup/seal/ajax/get_price.php"
    headers: Dict[str, str] = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    request_payload = {
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
        count[0] += 1
        return response

    else:
        print("Request failed with status code:", response.status_code)
        raise


def create_all_combinations(
    sizes: List[Dict[str, str]],
    print_papers: List[Dict[str, str]],
    paper_process_option: Dict[str, str],
) -> List[Dict[str, Union[str, None]]]:
    """
    すべてのサイズ、印刷用紙、加工オプションの組み合わせを生成する
    結果の例:
    {
        "category_id": str,
        "size_id": str,
        "paper_arr": str,
        "kakou": str,
        "tax_flag": 'true',
        # 追加情報
        "print_paper_name": str,
        "shape": str,
        "process": str,
    }[]
    """
    combinations: List[Dict[str, Union[str, None]]] = []
    for size in sizes:
        for print_pp in print_papers:
            possible_paper_process: List[int] = filter_paper_process_by_print_paper(print_pp["print_paper_id"])
            for process in possible_paper_process:
                # 一部の印刷用紙には異なるカスタマイズオプションがある
                print_paper_options = get_paper_id_arr(print_pp["print_paper_id"])
                if print_paper_options is None:
                    continue
                else:
                    for option in print_paper_options:
                        obj: Dict[str, Union[str, None]] = {
                            "category_id": str(generate_category_id(process)),
                            "size_id": size["size_id"],
                            "paper_arr": str(option),
                            "kakou": str(process),
                            "tax_flag": tax_flag,
                            # クエリに必要な情報以外の詳細
                            "print_paper_name": print_pp["print_paper_name"],
                            "shape": size["size"],
                            "process": paper_process_option.get(str(process)),
                        }
                        combinations.append(obj)

    return combinations

def crawl_label_seal_prices(
    formatter=lambda x: x,
    save_combinations: bool = False,
    save_crawl_data: bool = False,
    interval_s: float = 0.2,
) -> Dict:
    """
    ラベルとステッカーの価格をクロール
    save_combinations: すべての組み合わせをローカルファイルに保存するかどうか
    interval_s:       各リクエスト間の間隔
    """
    url = "https://www.printpac.co.jp/contents/lineup/seal/size.php"
    html: BeautifulSoup = get_webpage(url)

    # 1. すべてのサイズを取得（サイズは定数）
    size_divs: List[Tag] = get_all_paper_size_el(html)
    sizes: List[Dict[str, str]] = extract_all_sizes(size_divs)

    # 2. 印刷用紙（シールの紙質）を取得
    print_papers: List[Dict[str, str]] = extract_all_print_papers(html)
    paper_process_option: Dict[str, str] = get_paper_process_option(html)
    combinations: List[Dict[str, Union[str, None]]] = create_all_combinations(sizes, print_papers, paper_process_option)

    if save_combinations == True:
        with open("label_n_sticker_combination.txt", "w") as file:
            json.dump(combinations, file, indent=4)

    count = [0]
    res_data: Dict[str, Any] = {}

    for item in combinations:
        r: Response = get_price(item, count)
        if r is None:
            print("No data returned")
        else:
            res_data = r.json()["tbody"]["body"]

            for unit in res_data:
                for eigyo in res_data[unit]:
                    res_data[unit][eigyo]["SHAPE"] = item["shape"]
                    res_data[unit][eigyo]["PRINT"] = item["print_paper_name"]
                    res_data[unit][eigyo]["KAKOU"] = item["process"]
                    res_data[unit][eigyo]["UNIT"] = unit
                    res_data[unit][eigyo]["eigyo"] = eigyo
            time.sleep(interval_s)

    if save_crawl_data == True:
        with open("label_seal_crawl_result.txt", "w") as file:
            json.dump(res_data, file, indent=4)

    print("Success rate: ", count[0] * 100 / len(combinations))
    return formatter(res_data)
