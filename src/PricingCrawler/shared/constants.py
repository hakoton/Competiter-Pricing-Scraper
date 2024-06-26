from typing import Dict, Any
from enum import Enum


class Lamination(Enum):
    NO_LAMINATION = "ラミネートなし"
    GLOSSY_LAMINATED_PP = "光沢グロスPPラミネート"
    GLOSSY_LAMINATED_PP_WITH_WHITE_PLATE = "光沢グロスPPラミネート＋白版追加"
    MATTE_LAMINATED_PP = "マットPPラミネート"
    MATTE_LAMINATED_PP_WITH_WHITE_PLATE = "マットPPラミネート＋白版追加"
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
    """
    "正方形mm×mm",
    "長方形mm×mm",
    "角丸四角形mm×mm",
    "円形mm×mm",
    "楕円形mm×mm"
    """

    UNKNOWN = "unknown"  # Shapeは新しく、事前に定義されていません
    SQUARE = "正方形"
    RECTANGLE = "長方形"
    R_RECTANGLE = "角丸四角形"
    ROUND = "円形"
    OVAL = "楕円形"
    FREE = "free"
    MULTI = "multi"


class Color(Enum):
    FOUR_COLORS = "4 colors 1 side"
    FIVE_COLORS = "4 colors and white 1 side"


class ProducCategory(Enum):
    SEAL = 1
    STICKER = 2
    MULTI_STICKER = 3


"""
{
    [paper_group_id]: {
        [paper_id]: {
            "pid": int,
            "glue_type": Glue
        }
    }
}
印刷用紙IDと対応する用紙IDのマッピング
https://www.printpac.co.jp/contents/lineup/seal/js/size.js?20240612164729
"""
PID_TABLE: Dict[int, Dict[int, Dict[str, Any]]] = {
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
