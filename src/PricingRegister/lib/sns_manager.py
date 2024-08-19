from typing import List
import requests
from global_settings import GlobalSettings
from lib import ssm_manager
from shared.constants import (
    ProductCategory,
)
from shared.interfaces import PriceDiff
from shared.bigquery_mappings import (
    oid1,
    oid3,
)


class NotificationCenter:
    ssm: ssm_manager.Ssm
    slack_webhook_url: str

    def __init__(self, settings: GlobalSettings) -> None:
        self.ssm: ssm_manager.Ssm = ssm_manager.Ssm(settings)
        self.slack_webhook_url = self.ssm.get_slack_cred()

    def notify(
        self, product_name: ProductCategory, price_diff_list: List[PriceDiff]
    ) -> None:
        if len(price_diff_list) == 0:
            print("No price change found. Skip")
            return
        print(f"Number of price-changed items: {len(price_diff_list)}")

        """
        id = <oid1>_<oid2>_<oid3>_<shape>_<size>_<color>_<path>_<pid>_<eigyo>_<set>
        """
        message: str = (
            "--------------------------***--------------------------\n"
            f"商品: {product_name.value} \n"
        )

        price_change_content: str = ""
        for item in price_diff_list:
            id: str = item["composite_key"]
            parts = id.split("_")
            val_oid1 = parts[0]  # 加工
            # val_oid2 = parts[1]
            val_oid3 = parts[2]  # のり
            # val_shape = parts[3]
            val_size = parts[4]
            val_color = parts[5]
            val_path = parts[6]
            # val_pid = parts[7]
            val_eigyo = parts[8]
            val_set = parts[9]

            price_old: int = min(
                [
                    price
                    for price in [
                        item["old_actual_price"],
                        item["old_list_price"],
                        item["old_campaign_price"],
                    ]
                    if price != 0
                ]
            )

            price_new: int = min(
                [
                    price
                    for price in [
                        item["new_actual_price"],
                        item["new_list_price"],
                        item["new_campaign_price"],
                    ]
                    if price != 0
                ]
            )

            if price_old == price_new:
                continue

            raw_str = (
                "-----\n"
                "サイズ: <size> \n"
                "加工: <kakou> \n"
                "のり: <glue> \n"
                "色: <color>色 \n"
                "ハーフカット: <halfcut> \n"
                "営業: <eigyo>営業日 \n"
                "数量: <set>個 \n"
                "定価: <actual_price> \n"
            )

            price_change_content += (
                raw_str.replace("<product_name>", str(product_name.value))
                .replace("<size>", self._convert_size(product_name, val_size))
                .replace("<kakou>", self._find_str_value_from_mapping(val_oid1, oid1))
                .replace("<glue>", self._find_str_value_from_mapping(val_oid3, oid3))
                .replace("<color>", self._convert_color(val_color))
                .replace("<halfcut>", val_path)
                .replace("<eigyo>", val_eigyo)
                .replace("<set>", val_set)
                .replace(
                    "<actual_price>",
                    self._check_price_difference(price_old, price_new),
                )
            )
        message += price_change_content
        try:
            if len(price_change_content) == 0:
                return
            response: requests.Response = requests.post(
                self.slack_webhook_url,
                json={"text": message},
                headers={"Content-Type": "application/json"},
            )
            if response.status_code != 200:
                raise RuntimeError(response.text)
        except Exception as e:
            print(f"Error posting message: {e}")

    def _check_price_difference(self, price_old: int, price_new: int) -> str:
        if price_old == price_new:
            return f"{str(price_old)}円 (不変)"
        else:
            price_diff = price_old - price_new
            log = f"{str(price_old)}円 -> {str(price_new)}円 "
            if price_diff > 0:
                log += f"(値下: {abs(price_diff)}円)"
            else:
                log += f"(値上: {abs(price_diff)}円)"

            return log

    def _find_str_value_from_mapping(self, val, map_var: dict):
        reverse_mapping = {}
        for lamination, v in map_var.items():
            if str(v) not in reverse_mapping:
                reverse_mapping[str(v)] = []
            reverse_mapping[str(v)].append(lamination.value)

        result = reverse_mapping[str(val)]
        return str(result[0]) if len(result) == 1 else str(result)

    def _convert_size(self, product_category: ProductCategory, size: str) -> str:
        if product_category == ProductCategory.SEAL:
            # size = xxyy
            return size[0:2] + "mm x " + size[2:] + "mm"
        elif product_category == ProductCategory.STICKER:
            return "~" + size + "mm2"
        elif product_category == ProductCategory.MULTI_STICKER:
            return "A4サイズ" if size == "1003" else "はがきサイズ"
        else:
            return ""

    def _convert_color(self, color: str) -> str:
        return "5" if color == "50" else "4"
