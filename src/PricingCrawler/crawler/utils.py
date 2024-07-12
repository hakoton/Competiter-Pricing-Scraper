import requests
from requests import Response
from bs4 import BeautifulSoup, Tag
from typing import List, Union

from shared.interfaces import OptionInfo


def get_webpage(url: str) -> BeautifulSoup:
    try:
        response: Response = requests.get(url)
        response.raise_for_status()
        soup: BeautifulSoup = BeautifulSoup(response.content, "html.parser")
        return soup
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise e


def get_first_value_by_attr(el: Tag, field: str) -> str:
    """
    通常、タグから属性を取得する場合、型はUnion[str,List[str]]になります
    これは、'str'型で返される最初の値を強制的に取得するために使われます
    """
    val: Union[str, List[str]] = el[field]
    # 値が1つだけの場合
    if isinstance(val, str):
        return val
    elif isinstance(val, list) and val:  # valが空でないリストであるかを確認
        return val[0]
    else:
        raise ValueError("Invalid input")


def extract_id(data: List[OptionInfo]) -> List[str]:
    return [e["id"] for e in data]
