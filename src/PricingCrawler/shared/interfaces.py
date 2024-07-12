from typing import TypedDict, Union


class PriceSchema(TypedDict):
    yid: int
    oid1: int
    oid2: int
    oid3: int
    oid4: int
    shape: int
    size: str
    color: int
    path: str
    is_variable: bool
    pid: int
    weight: int
    day: int
    set: int
    List_price: int
    campaign_price: int
    Actual_price: int
    start_date: str


class OptionInfo(TypedDict):
    id: str
    name: str


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
    UNIT: str
    eigyo: str
    SHAPE: str
    PRINT: str
    KAKOU: str
    PAPER_GROUP_ID: str
    PAPER_ID: str


class StickerSizeSample(TypedDict):
    width: str
    height: str


class StickerSizeInfo(TypedDict):
    size_id: str
    size_sample: StickerSizeSample


class StickerCombination(TypedDict):
    """
    {
        "size_id": "69",
        "width": "10",
        "height": "120",
        "half_cut_amount_id": "2",
        "material_id": "1",
        "print_color_id": "1",
        "processing_opt_id":" 1
        "processing_opt_name":" ""
    }
    """

    size_id: str
    size_range: str
    width: str
    height: str

    print_color_id: str
    material_id: str
    processing_opt_id: str
    half_cut_amount_id: str
    processing_opt_name: str


class StickerRequestPayload(TypedDict):
    c_id: str
    size: str
    fix_size_w: str
    fix_size_h: str
    kami_mei: str
    irokazu: str
    houhou: str
    kakou1: str
    tax_flag: bool


class StickerPrice(TypedDict):
    """
    サーバーからのレスポンス
    Eg: {
        "s_id": "44243022",
        "t_id": "797248",
        "price": "1750",
        "price2": "2650",
        "tax": 159,
        "tax2": 241
    }
    """

    s_id: str
    t_id: str
    price: str
    price2: str
    tax: int
    tax2: int

    # 追加
    UNIT: str
    eigyo: str
    SIZE_RANGE: str
    SHAPE: str
    KAKOU: str
    KAKOU_NAME: str
    MATERIAL_ID: str
    COLOR_ID: str
    HALF_CUT: str


class MultiStickerRequestPayload(TypedDict):
    c_id: str
    irokazu_id: str
    houhou_id: str
    size_id: str
    kami_mei_id: str
    kakou1_id: Union[str, None]
    tax_flag: bool


class MultiStickerCombination(TypedDict):
    size_id: str
    print_color_id: str
    paper_id: str
    processing_opt_id: str
    processing_opt_name: str
    half_cut_amount_id: str


class MultiStickerPrice(TypedDict):
    """
    サーバーからのレスポンス
    Eg: {
        "s_id": "44243022",
        "t_id": "797248",
        "price": "1750",
        "price2": "2650",
        "tax": 159,
        "tax2": 241
    }
    """

    s_id: str
    t_id: str
    price: str
    price2: str
    tax: int
    tax2: int

    # 追加
    UNIT: str
    eigyo: str
    SHAPE: str
    SIZE_ID: str
    KAKOU: str
    KAKOU_NAME: str
    PAPER_ID: str
    COLOR_ID: str
    HALF_CUT: str
