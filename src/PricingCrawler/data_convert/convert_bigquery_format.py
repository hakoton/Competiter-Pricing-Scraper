from typing import Match, Union, Dict
import datetime
import re
from shared.constants import (
    Lamination,
    Form,
    Shape,
    Color,
    ProductCategory,
)
from shared.bigquery_mappings import (
    yid_fixed,
    oid1,
    oid2,
    oid3,
    oid4_fixed,
    shape,
    color,
    weight_fixed,
    MULTI_STICKER_PID_TABLE,
    STICKER_PID_TABLE,
    SEAL_PID_TABLE,
)
from shared.interfaces import MultiStickerPrice, PriceSchema, SealPrice, StickerPrice


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


def get_oid1(kakou: Lamination) -> int:
    result = oid1.get(kakou, oid1[Lamination.NOT_FOUND])
    if result == oid1[Lamination.NOT_FOUND]:
        print(f"Process opt: {kakou} is not supported")
    return result


def get_shape(paper_shape: str) -> int:
    for member in Shape:
        if member.value in paper_shape:
            result: int = shape.get(member, shape[Shape.UNKNOWN])
            if result == shape[Shape.UNKNOWN]:
                print(f"Unknown Shape: {paper_shape}")
            return result
    # shapeが見つからない場合、UNKNOWNを返す
    print(f"Unknown Shape: {paper_shape}")
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
        print(f"Unsupported seal's size: ${paper_shape}")
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
            r["oid1"] = get_oid1(item["KAKOU"])
            r["oid2"] = get_form(category)
            r["oid3"] = get_glue_id_seal(
                item["PAPER_GROUP_ID"],
                item["PAPER_ID"],
            )
            r["oid4"] = oid4_fixed
            r["shape"] = get_shape(item["SHAPE"])
            r["size"] = extract_seal_size(item["SHAPE"])
            r["color"] = (
                color[Color.FIVE_COLORS]
                if item["KAKOU"]
                in [
                    Lamination.WHITE_PLATE,
                    Lamination.GLOSSY_LAMINATED_PP_WITH_WHITE_PLATE,
                    Lamination.MATTE_LAMINATED_PP_WITH_WHITE_PLATE,
                ]
                else color[Color.FOUR_COLORS]
            )
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
            price = int(item["price"])
            price2 = int(item["price2"]) if item["price2"] is not None else None
            if price2 is None:
                r["List_price"] = price
                r["Actual_price"] = price
                r["campaign_price"] = 0
            else:
                r["List_price"] = price2
                r["Actual_price"] = price
                r["campaign_price"] = price

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
            r["oid1"] = get_oid1(item["KAKOU_NAME"])
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
            price = int(item["price"])
            price2 = int(item["price2"]) if item["price2"] is not None else None
            if price2 is None:
                r["List_price"] = price
                r["Actual_price"] = price
                r["campaign_price"] = 0
            else:
                r["List_price"] = price2
                r["Actual_price"] = price
                r["campaign_price"] = price

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
            r["oid1"] = get_oid1(item["KAKOU_NAME"])
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
            price = int(item["price"])
            price2 = int(item["price2"]) if item["price2"] is not None else None
            if price2 is None:
                r["List_price"] = price
                r["Actual_price"] = price
                r["campaign_price"] = 0
            else:
                r["List_price"] = price2
                r["Actual_price"] = price
                r["campaign_price"] = price

            r["start_date"] = s_date
            index[0] += 1
            records[index[0]] = r.copy()

    return records
