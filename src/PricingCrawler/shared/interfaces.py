from typing import TypedDict


class LabelSealRequestPayload(
    TypedDict(
        "LabelSealRequestPayload",
        {"paper_arr[]": str},
    ),
):
    category_id: str
    size_id: str
    kakou: str
    tax_flag: str


class SealCombination(TypedDict):
    """
    {
            "category_id": "91",
            "size_id": "628",
            "paper_arr": "173",
            "kakou": "5",
            "tax_flag": "false",

            "paper_name": "透明PETシール",
            "paper_group_id": "8",
            "shape": "楕円形75mm×50mm",
            "process": "光沢グロスPPラミネート＋白版追加"
        }
    """

    category_id: str
    size_id: str  #
    paper_arr: str
    kakou: str
    tax_flag: str
    # クエリに必要な情報以外の詳細
    paper_name: str
    paper_group_id: str
    shape: str
    process: str


class SealPrice(TypedDict):
    # サーバーからのレスポンス
    s_id: str
    price: int
    price2: int
    irokazu_id: str

    # 追加
    UNIT: int
    eigyo: int
    SHAPE: str
    PRINT: str
    KAKOU: str
    PAPER_GROUP_ID: str
    PAPER_ID: str
