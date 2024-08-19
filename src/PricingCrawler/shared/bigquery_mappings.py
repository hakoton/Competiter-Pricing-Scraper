from typing import Any, Union, Dict
from shared.constants import (
    Lamination,
    Form,
    Glue,
    PidAndGlueInfo,
    Shape,
    Color,
)

yid_fixed = 21  # 固定
oid1: Dict[Union[Lamination, str], int] = {
    Lamination.NOT_FOUND: 0,
    Lamination.NO_LAMINATION: 1,
    Lamination.WHITE_PLATE: 1,
    Lamination.GLOSSY_LAMINATED: 2,
    Lamination.GLOSSY_LAMINATED_PP: 2,
    Lamination.GLOSSY_LAMINATED_PP_WITH_WHITE_PLATE: 2,
    Lamination.MATTE_LAMINATED: 5,
    Lamination.MATTE_LAMINATED_PP: 5,
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

SEAL_PID_TABLE: Dict[int, Dict[int, Dict[str, Any]]] = {
    1: {152: {"pid": 100, "glue_type": Glue.REPEELABLE_GLUE}},
    2: {154: {"pid": 204, "glue_type": Glue.ORDINARY_GLUE}},
    3: {153: {"pid": 100, "glue_type": Glue.CORRECTION_GLUE}},
    4: {157: {"pid": 100, "glue_type": Glue.FROZEN_FOOD_PASTE}},
    5: {155: {"pid": 101, "glue_type": Glue.ORDINARY_GLUE}},
    6: {158: {"pid": 224, "glue_type": Glue.ORDINARY_GLUE}},
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


STICKER_SIZE_TABLE: Any = {
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
