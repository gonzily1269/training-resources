"""注文APIが返すHTTPレスポンススキーマを定義する。"""

from pydantic import BaseModel


class OrderResponse(BaseModel):
    """注文情報と配送状況を表すAPIレスポンス。

    Attributes:
        orderId: 注文の識別子。
        customerName: 顧客名。
        deliveryStatus: 外部配送APIから取得した配送状況。
    """

    orderId: int
    customerName: str
    deliveryStatus: str
