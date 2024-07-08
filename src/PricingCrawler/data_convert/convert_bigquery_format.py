from typing import Match, Union, Dict
import datetime
import re
from shared.constants import (
    Lamination,
    Form,
    Glue,
    Shape,
    Color,
    ProducCategory,
    PID_TABLE,
)
from shared.interfaces import SealPrice


yid_fixed = 21  # 固定
oid1: Dict[Union[Lamination, str], int] = {
    Lamination.NO_LAMINATION: 1,
    Lamination.GLOSSY_LAMINATED_PP: 2,
    Lamination.GLOSSY_LAMINATED_PP_WITH_WHITE_PLATE: 2,
    Lamination.MATTE_LAMINATED_PP: 5,
    Lamination.MATTE_LAMINATED_PP_WITH_WHITE_PLATE: 5,
    # 以下の文字列は、利用可能なオプションではないため、ウェブサイト上の値と一致するかどうか検証されません。
    Lamination.GLOSSY_LAMINATED_PVC: 3,
    Lamination.GLOSSY_LAMINATED_PET: 4,
    Lamination.MATTE_LAMINATED_PVC: 6,
    Lamination.MATTE_LAMINATED_PET: 7,
}
oid2: Dict[Form, int] = {
    Form.MULTI_SHEETS_ON_ONE: 80,
    Form.ROSE_SQUARE_CUT: 81,
    Form.ROSE_MOUNT_CUT: 82,
    Form.ROLL_SEAL: 83,
}
oid3: Dict[Glue, int] = {
    Glue.ORDINARY_GLUE: 1,
    Glue.STRONG_ADHESIVE: 2,
    Glue.CORRECTION_GLUE: 3,
    Glue.REPEELABLE_GLUE: 4,
    Glue.FROZEN_FOOD_PASTE: 5,
    Glue.STRONG_ADHESIVE_FIBER_GLUE: 6,
    Glue.FROZEN_GLUE: 7,
}
oid4_fixed = 1  # 固定

shape: Dict[Union[Shape, str], int] = {
    Shape.UNKNOWN: 0,
    Shape.SQUARE: 1,
    Shape.RECTANGLE: 2,
    Shape.R_RECTANGLE: 3,
    Shape.ROUND: 4,
    Shape.OVAL: 5,
    Shape.FREE: 6,
    Shape.MULTI: 7,
}

color: Dict[Color, int] = {Color.FOUR_COLORS: 40, Color.FIVE_COLORS: 50}
weight_fixed = 0  # 固定


def get_shape(paper_shape: str) -> int:
    for member in Shape:
        if member.value in paper_shape:
            result: int = shape.get(member, shape[Shape.UNKNOWN])
            return result
    # shapeが見つからない場合、UNKNOWNを返す
    return shape[Shape.UNKNOWN]


def get_form(category: ProducCategory) -> int:
    if category == ProducCategory:
        return oid2[Form.MULTI_SHEETS_ON_ONE]
    else:
        return oid2[Form.ROSE_MOUNT_CUT]


def get_glue_id(paper_group: str, paper_id: str) -> int:
    val = oid3[PID_TABLE[int(paper_group)][int(paper_id)]["glue_type"]]
    if val:
        return val
    else:
        print("[PID] Paper not found - group={}, id={} ".format(paper_group, paper_id))
        return -1


def extract_size(paper_shape: str) -> str:
    match: Union[Match[str], None] = re.search(r"\d+mm×\d+mm", paper_shape)
    if match:
        extracted_value: str = match.group(0)  # 60mmx60mm
        dimension: str = extracted_value[:2] + extracted_value[5:7]  # 6060
        return dimension
    else:
        return "Unknown"


# 白版
def include_white_layer(processing: str) -> bool:
    if "白版" in processing:
        return True
    else:
        return False


def get_half_cut(category: ProducCategory) -> int:
    """
    seal: 0
    sticker: 0 -> 3
    multi sticker: 0 -> 10
    """
    if category == ProducCategory.SEAL:
        return 0
    # TODO: 他のカテゴリ
    else:
        return 1


def is_variable_in_size(category: ProducCategory) -> int:
    if category == ProducCategory.SEAL:
        return False
    else:
        return True


def get_pid(paper_group: str, paper_id: str) -> int:
    val = PID_TABLE[int(paper_group)][int(paper_id)]["pid"]
    if val:
        return val
    else:
        print("[PID] Paper not found - group={}, id={} ".format(paper_group, paper_id))
        return -1


def convert_for_bigquery(
    category: ProducCategory,
    raw_data: Dict[int, Dict[int, SealPrice]],
    index,
) -> Dict:
    """
    raw_data :Dict[UNIT, Dict[eigyo: SealPrice]]
    """
    SCHEMA_SEAL: Dict = {
        "yid": 0,
        "oid1": 0,
        "oid2": 0,
        "oid3": 0,
        "oid4": 0,
        "shape": "",
        "size": "",
        "color": 0,
        "path": 0,
        "is_variable": False,
        "pid": 0,
        "weight": 0,
        "day": 0,
        "set": 0,
        "List_price": 0,
        "campaign_price": 0,
        "Actual_price": 0,
        "start_date": "2024-06-20",
    }

    records: Dict = {}
    s_date: str = datetime.date.today().strftime("%Y-%m-%d")
    for unit in raw_data:
        for eigyo in raw_data[unit]:
            item = raw_data[unit][eigyo]
            r: Dict = SCHEMA_SEAL
            r["yid"] = yid_fixed
            r["oid1"] = oid1.get(item["KAKOU"], oid1[Lamination.NO_LAMINATION])
            r["oid2"] = get_form(category)
            r["oid3"] = get_glue_id(
                item["PAPER_GROUP_ID"],
                item["PAPER_ID"],
            )
            r["oid4"] = oid4_fixed
            r["shape"] = get_shape(item["SHAPE"])
            r["size"] = extract_size(item["SHAPE"])
            r["color"] = (
                color[Color.FOUR_COLORS]
                if include_white_layer(item["KAKOU"])
                else color[Color.FIVE_COLORS]
            )
            r["path"] = get_half_cut(category)
            r["is_variable"] = is_variable_in_size(category)
            r["pid"] = get_pid(
                item["PAPER_GROUP_ID"],
                item["PAPER_ID"],
            )

            r["weight"] = weight_fixed
            r["day"] = int(eigyo)
            r["set"] = int(unit)
            """
            キャンペーンなし:
                price  = 定価
                price2 = null
            キャンペーンあり:
                price  = キャンペーン価格
                price2 = 定価
            """
            price: int = item["price"]
            price2: int = item["price2"]
            if price2 is None:
                list_price: int = price
                campaign_price: int = list_price
            else:
                list_price: int = price2
                campaign_price: int = price
            r["List_price"] = list_price
            r["campaign_price"] = campaign_price
            r["Actual_price"] = list_price

            r["start_date"] = s_date
            index[0] += 1
            records[index[0]] = r.copy()

    return records
