"""DBやWebフレームワークに依存しない注文ドメインモデルを定義する。"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Order:
    """注文の業務情報を表す不変のドメインモデル。

    Attributes:
        id: 注文の識別子。
        customer_name: 顧客名。
        update_at: 注文情報の最終更新日時。
    """

    id: int
    customer_name: str
    update_at: datetime
