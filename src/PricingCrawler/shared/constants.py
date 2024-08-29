from typing import TypedDict
from enum import Enum


class Lamination(Enum):
    NOT_FOUND = "NOT_FOUND"
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
    SEAL = "シール"
    STICKER = "ステッカー"
    MULTI_STICKER = "マルチステッカー"


class PidAndGlueInfo(TypedDict):
    pid: int
    glue_type: Glue
