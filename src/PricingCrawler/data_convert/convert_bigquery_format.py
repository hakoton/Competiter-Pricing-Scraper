from typing import Match, Union, Dict
import datetime
import re
import math
from shared.constants import (
    MULTI_STICKER_PID_TABLE,
    STICKER_PID_TABLE,
    Lamination,
    Form,
    Glue,
    Shape,
    Color,
    ProductCategory,
    SEAL_PID_TABLE,
)
from shared.interfaces import MultiStickerPrice, PriceSchema, SealPrice, StickerPrice


yid_fixed = 21  # 固定
oid1: Dict[Union[Lamination, str], int] = {
    Lamination.NO_LAMINATION: 1,
    Lamination.GLOSSY_LAMINATED_PP: 2,
    Lamination.GLOSSY_LAMINATED_PP_WITH_WHITE_PLATE: 2,
    Lamination.MATTE_LAMINATED: 2,
    Lamination.MATTE_LAMINATED_PP: 5,
    Lamination.MATTE_LAMINATED: 5,
    Lamination.MATTE_LAMINATED_PP_WITH_WHITE_PLATE: 5,
    Lamination.EMBOSSED_LAMINATED: 1000,
    # 以下の文字列は、利用可能なオプションではないため、ウェブサイト上の値と一致するかどうか検証されません。
    Lamination.GLOSSY_LAMINATED_PVC: 3,
    Lamination.GLOSSY_LAMINATED_PET: 4,
    Lamination.MATTE_LAMINATED_PVC: 6,
    Lamination.MATTE_LAMINATED_PET: 7,
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

SCHEMA_SEAL: PriceSchema = {
    "yid": 0,
    "oid1": 0,
    "oid2": 0,
    "oid3": 0,
    "oid4": 0,
    "shape": 0,
    "size": "",
    "color": 0,
    "path": "",
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


def get_shape(paper_shape: str) -> int:
    for member in Shape:
        if member.value in paper_shape:
            result: int = shape.get(member, shape[Shape.UNKNOWN])
            return result
    # shapeが見つからない場合、UNKNOWNを返す
    return shape[Shape.UNKNOWN]


def get_form(category: ProductCategory) -> int:
    # 自由サイズ
    if category == ProductCategory.STICKER:
        return oid2[Form.ROSE_MOUNT_CUT]
    # 固定サイズ
    else:
        return oid2[Form.MULTI_SHEETS_ON_ONE]


def get_glue_id_seal(paper_group: str, paper_id: str) -> int:
    val: int = oid3[SEAL_PID_TABLE[int(paper_group)][int(paper_id)]["glue_type"]]
    if val:
        return val
    else:
        print("[PID] Paper not found - group={}, id={} ".format(paper_group, paper_id))
        return -1


def get_glue_id_sticker(material_id: str) -> int:
    val: int = oid3[STICKER_PID_TABLE[int(material_id)]["glue_type"]]
    if val:
        return val
    else:
        print("[PID] Paper not found - material_id={}, id={} ".format(material_id))
        return -1


def get_glue_id_multi_sticker(paper_id: str) -> int:
    val: int = oid3[MULTI_STICKER_PID_TABLE[int(paper_id)]["glue_type"]]
    if val:
        return val
    else:
        print("[PID] Paper not found - paper_id={}, id={} ".format(paper_id))
        return -1


def extract_seal_size(paper_shape: str) -> str:
    match: Union[Match[str], None] = re.search(r"\d+mm×\d+mm", paper_shape)
    if match:
        extracted_value: str = match.group(0)  # 60mmx60mm
        dimension: str = extracted_value[:2] + extracted_value[5:7]  # 6060
        return dimension
    else:
        return "Unknown"


def get_half_cut_multi_sticker(halfcut_id: str) -> str:
    mapping = {
        "1": "0~3",
        "2": "4~7",
        "3": "8~10",
        "4": "11~15",
        "5": "16~20",
    }
    return mapping[halfcut_id]


def is_variable_in_size(category: ProductCategory) -> bool:
    if category == ProductCategory.SEAL:
        return False
    else:
        return True


def get_pid_seal(paper_group: str, paper_id: str) -> int:
    val = SEAL_PID_TABLE[int(paper_group)][int(paper_id)]["pid"]
    if val:
        return val
    else:
        print("[PID] Paper not found - group={}, id={} ".format(paper_group, paper_id))
        return -1


def get_pid_sticker(material_id: str) -> int:
    return STICKER_PID_TABLE[int(material_id)]["pid"]


def get_pid_multi_sticker(material_id: str) -> int:
    return MULTI_STICKER_PID_TABLE[int(material_id)]["pid"]


def convert_seal_price_for_bigquery(
    category: ProductCategory,
    raw_data: Dict[str, Dict[str, SealPrice]],
    index,
) -> Dict:
    records: Dict = {}
    s_date: str = datetime.date.today().strftime("%Y-%m-%d")
    for unit in raw_data:
        for eigyo in raw_data[unit]:
            item = raw_data[unit][eigyo]
            r: PriceSchema = SCHEMA_SEAL
            r["yid"] = yid_fixed
            r["oid1"] = oid1.get(item["KAKOU"], oid1[Lamination.NO_LAMINATION])
            r["oid2"] = get_form(category)
            r["oid3"] = get_glue_id_seal(
                item["PAPER_GROUP_ID"],
                item["PAPER_ID"],
            )
            r["oid4"] = oid4_fixed
            r["shape"] = get_shape(item["SHAPE"])
            r["size"] = extract_seal_size(item["SHAPE"])
            r["color"] = color[Color.FOUR_COLORS]
            r["path"] = "0"
            r["is_variable"] = is_variable_in_size(category)
            r["pid"] = get_pid_seal(
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


def convert_sticker_price_for_bigquery(
    category: ProductCategory,
    raw_data: Dict[str, Dict[str, StickerPrice]],
    index,
) -> Dict:
    records: Dict = {}
    s_date: str = datetime.date.today().strftime("%Y-%m-%d")
    for unit in raw_data:
        for eigyo in raw_data[unit]:
            item: StickerPrice = raw_data[unit][eigyo]
            r: PriceSchema = SCHEMA_SEAL
            r["yid"] = yid_fixed
            r["oid1"] = oid1.get(item["KAKOU_NAME"], oid1[Lamination.NO_LAMINATION])
            r["oid2"] = get_form(category)
            r["oid3"] = get_glue_id_sticker(item["MATERIAL_ID"])
            r["oid4"] = oid4_fixed
            r["shape"] = get_shape(item["SHAPE"])
            r["size"] = item["SIZE_RANGE"]
            r["color"] = (
                color[Color.FOUR_COLORS]
                if item["COLOR_ID"] == Color.FOUR_COLORS.value
                else color[Color.FIVE_COLORS]
            )
            r["path"] = item["HALF_CUT"]
            r["is_variable"] = is_variable_in_size(category)
            r["pid"] = get_pid_sticker(item["MATERIAL_ID"])

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
            price: int = int(item["price"])
            price2: int = int(item["price2"])
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


def convert_multi_sticker_price_for_bigquery(
    category: ProductCategory,
    raw_data: Dict[str, Dict[str, MultiStickerPrice]],
    index,
) -> Dict:
    records: Dict = {}
    s_date: str = datetime.date.today().strftime("%Y-%m-%d")
    for unit in raw_data:
        for eigyo in raw_data[unit]:
            item: MultiStickerPrice = raw_data[unit][eigyo]
            r: PriceSchema = SCHEMA_SEAL
            r["yid"] = yid_fixed
            r["oid1"] = oid1.get(item["KAKOU_NAME"], oid1[Lamination.NO_LAMINATION])
            r["oid2"] = get_form(category)
            r["oid3"] = get_glue_id_multi_sticker(item["PAPER_ID"])
            r["oid4"] = oid4_fixed
            r["shape"] = get_shape(item["SHAPE"])
            r["size"] = (
                "1003" if item["SIZE_ID"] == "4" else "1023"
            )  # マッピングはウェブサイトのスクリプトから取得されます
            r["color"] = (
                color[Color.FOUR_COLORS]
                if item["COLOR_ID"] == Color.FOUR_COLORS.value
                else color[Color.FIVE_COLORS]
            )
            r["path"] = get_half_cut_multi_sticker(item["HALF_CUT"])
            r["is_variable"] = is_variable_in_size(category)
            r["pid"] = get_pid_multi_sticker(item["PAPER_ID"])

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
            price: int = int(item["price"])
            price2: int = int(item["price2"])
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


def convert_ondemand_envelope_price_for_bigquery(
    raw_data,
    index
) -> Dict:
    records: Dict = {}
    s_date: str = datetime.date.today().strftime("%Y-%m-%d")

    request = raw_data["body"]
    oid_map = {
        1: ["204", "351", "352", "223"],
        2: ["203", "350"]
    }
    sid_map = {
        28: ["63"],
        33: ["67"]
    }
    pid_map = {
        106: ["204", "203"],
        105: ["350", "351"],
        294: ["352"],
        169: ["223"]
    }
    weight_map = {
        85: ["204", "203"],
        80: ["350", "351"],
        100: ["352", "223"]
    }

    color_map = {
        # 片面スミ一色
        10: [5],
        # 両面スミ一色
        11: [6],
        # 片面4色
        40: [1],
        # 表4色裏1色
        41: [2],
        # 両面4色
        44: [4]
    }
    r: PriceSchema = SCHEMA_SEAL
    r["yid"] = 7
    r["oid1"] = next((k for k, v in oid_map.items() if request["kami_mei_id"] in v), None)
    r["oid2"] = 1
    r["oid3"] = 4
    r["oid4"] = 1
    r["sid"] = next((k for k, v in sid_map.items() if request["size_id"] in v), None)
    r["pid"] = next((k for k, v in pid_map.items() if request["kami_mei_id"] in v), None)
    r["print_method"] = 2
    r["weight"] = next((k for k, v in weight_map.items() if request["kami_mei_id"] in v), None)
    res_data = raw_data["tbody"]["body"]
    for unit in res_data:
        for eigyo in res_data[unit]:
            for color in res_data[unit][eigyo]:
                item = res_data[unit][eigyo][color]
                r["day"] = int(eigyo)
                r["set"] = int(unit)
                r["color"] = next((k for k, v in color_map.items() if int(color) in v), None)
                tax_excluded_price: int = math.ceil(int(item["price"]) / 1.1) # 税抜き価格
                r["List_price"] = tax_excluded_price
                r["campaign_price"] = tax_excluded_price
                r["Actual_price"] = tax_excluded_price

                r["start_date"] = s_date
                index[0] += 1
                records[index[0]] = r.copy()

    return records
