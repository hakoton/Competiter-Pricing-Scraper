from typing import Dict, Any, TypedDict, List
from enum import Enum

from shared.interfaces import StickerSizeInfo


class Lamination(Enum):
    NO_LAMINATION = "ラミネートなし"
    WHITE_PLATE = "白版追加"
    GLOSSY_LAMINATED = "つや ラミネート"
    GLOSSY_LAMINATED_PP = "光沢グロスPPラミネート"
    GLOSSY_LAMINATED_PP_WITH_WHITE_PLATE = "光沢グロスPPラミネート＋白版追加"
    MATTE_LAMINATED_PP = "マットPPラミネート"
    MATTE_LAMINATED_PP_WITH_WHITE_PLATE = "マットPPラミネート＋白版追加"
    MATTE_LAMINATED = "マット ラミネート"
    EMBOSSED_LAMINATED = "エンボス ラミネート"

    # 以下の文字列は、利用可能なオプションではないため、ウェブサイト上の値と一致するかどうか検証されません。
    GLOSSY_LAMINATED_PVC = "光沢ラミネート加工（PVC）"
    GLOSSY_LAMINATED_PET = "光沢ラミネート(PET)"
    MATTE_LAMINATED_PVC = "マットラミネート(PVC)"
    MATTE_LAMINATED_PET = "マットラミネート(PET)"


class Form(Enum):
    MULTI_SHEETS_ON_ONE = "1シートに複数枚"
    ROSE_SQUARE_CUT = "バラ四角カット"
    ROSE_MOUNT_CUT = "バラ台紙カット"
    ROLL_SEAL = "ロールシール"


class Glue(Enum):
    ORDINARY_GLUE = "普通のり"
    STRONG_ADHESIVE = "強粘着"
    CORRECTION_GLUE = "訂正のり"
    REPEELABLE_GLUE = "再剥離のり"
    FROZEN_FOOD_PASTE = "冷食のり"
    STRONG_ADHESIVE_FIBER_GLUE = "強粘着(センイ)のり"
    FROZEN_GLUE = "冷凍用（冷凍のり）"


class Shape(Enum):
    UNKNOWN = "unknown"  # Shapeは新しく、事前に定義されていません
    SQUARE = "正方形"
    RECTANGLE = "長方形"
    R_RECTANGLE = "角丸四角形"
    ROUND = "円形"
    OVAL = "楕円形"
    FREE = "自由"
    MULTI = "multi"


class Color(Enum):
    FOUR_COLORS = "1"  # CMYK印刷
    FIVE_COLORS = "2"  # RGB+α印刷


class ProductCategory(Enum):
    SEAL = 1
    STICKER = 2
    MULTI_STICKER = 3


class PidAndGlueInfo(TypedDict):
    pid: int
    glue_type: Glue


"""
印刷用紙IDと対応する用紙IDのマッピング
https://www.printpac.co.jp/contents/lineup/seal/js/size.js?20240612164729
{
    [paper_group_id]: {
        [paper_id]: {
            "pid": int,
            "glue_type": Glue
        }
    }
}
"""
SEAL_PID_TABLE: Dict[int, Dict[int, Dict[str, Any]]] = {
    1: {152: {"pid": 100, "glue_type": Glue.REPEELABLE_GLUE}},
    2: {154: {"pid": 204, "glue_type": Glue.ORDINARY_GLUE}},
    3: {153: {"pid": 100, "glue_type": Glue.CORRECTION_GLUE}},
    4: {157: {"pid": 100, "glue_type": Glue.FROZEN_FOOD_PASTE}},
    5: {155: {"pid": 101, "glue_type": Glue.ORDINARY_GLUE}},
    6: {158: {"pid": 222, "glue_type": Glue.ORDINARY_GLUE}},
    7: {156: {"pid": 237, "glue_type": Glue.ORDINARY_GLUE}},
    8: {173: {"pid": 238, "glue_type": Glue.ORDINARY_GLUE}},
    9: {147: {"pid": 222, "glue_type": Glue.ORDINARY_GLUE}},
    10: {148: {"pid": 1011, "glue_type": Glue.ORDINARY_GLUE}},
    11: {159: {"pid": 106, "glue_type": Glue.ORDINARY_GLUE}},
    12: {174: {"pid": 289, "glue_type": Glue.STRONG_ADHESIVE}},
    13: {
        419: {"pid": 1005, "glue_type": Glue.ORDINARY_GLUE},
        432: {"pid": 1008, "glue_type": Glue.ORDINARY_GLUE},
        433: {"pid": 1006, "glue_type": Glue.ORDINARY_GLUE},
        434: {"pid": 1007, "glue_type": Glue.ORDINARY_GLUE},
        435: {"pid": 1004, "glue_type": Glue.ORDINARY_GLUE},
    },
    14: {
        175: {"pid": 252, "glue_type": Glue.STRONG_ADHESIVE},
        176: {"pid": 1015, "glue_type": Glue.STRONG_ADHESIVE},
        177: {"pid": 251, "glue_type": Glue.STRONG_ADHESIVE},
        178: {"pid": 290, "glue_type": Glue.STRONG_ADHESIVE},
        179: {"pid": 250, "glue_type": Glue.STRONG_ADHESIVE},
    },
    15: {
        417: {"pid": 239, "glue_type": Glue.ORDINARY_GLUE},
        418: {"pid": 241, "glue_type": Glue.ORDINARY_GLUE},
    },
    16: {194: {"pid": 1016, "glue_type": Glue.CORRECTION_GLUE}},
    17: {192: {"pid": 101, "glue_type": Glue.CORRECTION_GLUE}},
    18: {193: {"pid": 204, "glue_type": Glue.CORRECTION_GLUE}},
    19: {
        415: {"pid": 240, "glue_type": Glue.ORDINARY_GLUE},
        416: {"pid": 242, "glue_type": Glue.ORDINARY_GLUE},
    },
    21: {472: {"pid": 1010, "glue_type": Glue.ORDINARY_GLUE}},
    23: {473: {"pid": 1012, "glue_type": Glue.ORDINARY_GLUE}},
    24: {471: {"pid": 1014, "glue_type": Glue.ORDINARY_GLUE}},
    25: {474: {"pid": 1013, "glue_type": Glue.ORDINARY_GLUE}},
    26: {470: {"pid": 1009, "glue_type": Glue.ORDINARY_GLUE}},
}


STICKER_SIZE_TABLE: Dict[str, StickerSizeInfo] = {
    "1250": {"size_id": "69", "size_sample": {"width": "10", "height": "120"}},
    "2500": {"size_id": "70", "size_sample": {"width": "10", "height": "200"}},
    "5000": {"size_id": "71", "size_sample": {"width": "10", "height": "400"}},
    "10000": {"size_id": "72", "size_sample": {"width": "10", "height": "900"}},
    "15000": {"size_id": "73", "size_sample": {"width": "10", "height": "1400"}},
    "22500": {"size_id": "74", "size_sample": {"width": "10", "height": "2200"}},
    "30000": {"size_id": "75", "size_sample": {"width": "10", "height": "2900"}},
    "40000": {"size_id": "76", "size_sample": {"width": "10", "height": "3900"}},
    "60000": {"size_id": "77", "size_sample": {"width": "10", "height": "5900"}},
    "90000": {"size_id": "78", "size_sample": {"width": "10", "height": "8900"}},
}


"""
{
    [material_id]: {
        "pid": int,
        "glue_type": Glue
    }
}
"""
STICKER_PID_TABLE: Dict[int, PidAndGlueInfo] = {
    1: {"pid": 237, "glue_type": Glue.CORRECTION_GLUE},  # 合成紙（グレー糊）
    2: {"pid": 224, "glue_type": Glue.ORDINARY_GLUE},  # PET
    3: {"pid": 207, "glue_type": Glue.STRONG_ADHESIVE},  # 塩ビ（ツヤ）
    4: {"pid": 1002, "glue_type": Glue.ORDINARY_GLUE},  # 塩ビ（マット）
    5: {"pid": 1001, "glue_type": Glue.ORDINARY_GLUE},  # 塩ビ（ツヤlite）
    6: {"pid": 1003, "glue_type": Glue.REPEELABLE_GLUE},  # 塩ビ（ツヤ）強粘着
}

"""
{
    [paper_id]: {
        "pid": int,
        "glue_type": Glue
    }
}
"""
MULTI_STICKER_PID_TABLE: Dict[int, PidAndGlueInfo] = {
    404: {"pid": 207, "glue_type": Glue.STRONG_ADHESIVE},  # 塩ビ（ツヤ）
    405: {"pid": 224, "glue_type": Glue.ORDINARY_GLUE},  # PET
    409: {"pid": 1001, "glue_type": Glue.ORDINARY_GLUE},  # 塩ビ（ツヤlite）
}

"""
以下は封筒に関する定義とマッピング
https://www.printpac.co.jp/contents/lineup/ondemand_envelope/price.php
https://www.printpac.co.jp/contents/lineup/envelope/price.php
"""
# ラクスルのID
class EnvelopeOidRaksul(Enum):
    POSTAL_CODE_INCLUDE = 1
    POSTAL_CODE_NONE = 2
class EnvelopeSidRaksul(Enum):
    NAGA3 = 28
    KAKU2 = 33
class EnvelopePidRaksul(Enum):
    KRAFT = 106
    WHITE_KENT = 105
    WHITE_KENT100 = 294
    PRIVACY = 169
class EnvelopeColorRaksul(Enum):
    SINGLE_MONOCHROME = 10  # 片面スミ一色
    DOUBLE_MONOCHROME = 11  # 両面スミ一色
    SINGLE_COLOR = 40       # 片面4色
    COLOR_MONOCHROME = 41   # 表4色裏1色
    DOUBLE_COLOR = 44       # 両面4色

# プリントパックのID
class EnvelopePaperPrintpac(Enum):
    KRAFT85_POSTAL_CODE_NONE = 204
    KRAFT85_POSTAL_CODE_INCLUDE = 203
    WHITE_KENT80_POSTAL_CODE_NONE = 351
    WHITE_KENT80_POSTAL_CODE_INCLUDE = 350
    WHITE_KENT100_POSTAL_CODE_NONE = 352
    PRIVACY100_POSTAL_CODE_NONE = 223
class EnvelopeSizePrintpac(Enum):
    NAGA3 = 63
    KAKU2 = 67
class EnvelopeColorPrintpac(Enum):
    SINGLE_MONOCHROME = 5   # 片面スミ一色
    DOUBLE_MONOCHROME = 6   # 両面スミ一色
    SINGLE_COLOR = 1        # 片面4色
    COLOR_MONOCHROME = 2    # 表4色裏1色
    DOUBLE_COLOR = 4        # 両面4色

# ラクスルIDとプリントパックIDのマッピング
ENVELOPE_OID1_TABLE: Dict[int, List[str]] = {
    EnvelopeOidRaksul.POSTAL_CODE_NONE: [
        EnvelopePaperPrintpac.KRAFT85_POSTAL_CODE_NONE,
        EnvelopePaperPrintpac.WHITE_KENT80_POSTAL_CODE_NONE,
        EnvelopePaperPrintpac.WHITE_KENT100_POSTAL_CODE_NONE,
        EnvelopePaperPrintpac.PRIVACY100_POSTAL_CODE_NONE,
    ],
    EnvelopeOidRaksul.POSTAL_CODE_INCLUDE: [
        EnvelopePaperPrintpac.KRAFT85_POSTAL_CODE_INCLUDE,
        EnvelopePaperPrintpac.WHITE_KENT80_POSTAL_CODE_INCLUDE,
    ],
}

ENVELOPE_SID_TABLE: Dict[int, Dict[int, List[str]]] = {
    EnvelopeSidRaksul.NAGA3: [
        EnvelopeSizePrintpac.NAGA3,
    ],
    EnvelopeSidRaksul.KAKU2: [
        EnvelopeSizePrintpac.KAKU2,
    ],
}

ENVELOPE_PID_TABLE: Dict[int, Dict[int, List[str]]] = {
    EnvelopePidRaksul.KRAFT: [
        EnvelopePaperPrintpac.KRAFT85_POSTAL_CODE_NONE,
        EnvelopePaperPrintpac.KRAFT85_POSTAL_CODE_INCLUDE,
    ],
    EnvelopePidRaksul.WHITE_KENT: [
        EnvelopePaperPrintpac.WHITE_KENT80_POSTAL_CODE_NONE,
        EnvelopePaperPrintpac.WHITE_KENT80_POSTAL_CODE_INCLUDE,
    ],
    EnvelopePidRaksul.WHITE_KENT100: [
        EnvelopePaperPrintpac.WHITE_KENT100_POSTAL_CODE_NONE,
    ],
    EnvelopePidRaksul.PRIVACY: [
        EnvelopePaperPrintpac.PRIVACY100_POSTAL_CODE_NONE,
    ],
}

ENVELOPE_WEIGHT_TABLE: Dict[int, List[str]] = {
    85: [
        EnvelopePaperPrintpac.KRAFT85_POSTAL_CODE_NONE,
        EnvelopePaperPrintpac.KRAFT85_POSTAL_CODE_INCLUDE,
    ],
    80: [
        EnvelopePaperPrintpac.WHITE_KENT80_POSTAL_CODE_NONE,
        EnvelopePaperPrintpac.WHITE_KENT80_POSTAL_CODE_INCLUDE,
    ],
    100:[
        EnvelopePaperPrintpac.WHITE_KENT100_POSTAL_CODE_NONE,
        EnvelopePaperPrintpac.PRIVACY100_POSTAL_CODE_NONE,
    ]
}

ENVELOPE_COLOR_TABLE: Dict[int, List[str]] = {
    EnvelopeColorRaksul.SINGLE_MONOCHROME: [
        EnvelopeColorPrintpac.SINGLE_MONOCHROME
    ],
    EnvelopeColorRaksul.DOUBLE_MONOCHROME: [
        EnvelopeColorPrintpac.DOUBLE_MONOCHROME
    ],
    EnvelopeColorRaksul.SINGLE_COLOR: [
        EnvelopeColorPrintpac.SINGLE_COLOR
    ],
    EnvelopeColorRaksul.COLOR_MONOCHROME: [
        EnvelopeColorPrintpac.COLOR_MONOCHROME
    ],
    EnvelopeColorRaksul.DOUBLE_COLOR: [
        EnvelopeColorPrintpac.DOUBLE_COLOR
    ]
}

