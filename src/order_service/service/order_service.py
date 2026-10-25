"""注文取得ユースケースとその結果を定義する。"""

from dataclasses import dataclass

from order_service.external import DeliveryApiClient
from order_service.model import Order
from order_service.repository import OrderRepository


@dataclass(frozen=True)
class OrderResult:
    """注文と外部配送APIの状況を組み合わせたユースケース結果。

    Attributes:
        order_id: 注文の識別子。
        customer_name: 顧客名。
        delivery_status: 外部配送APIから取得した配送状況。
    """

    order_id: int
    customer_name: str
    delivery_status: str


class OrderService:
    """注文の取得と配送状況の照会を組み合わせる。"""

    def __init__(
        self,
        order_repository: OrderRepository,
        delivery_api_client: DeliveryApiClient,
    ) -> None:
        """注文Repositoryと配送APIクライアントを受け取る。

        Args:
            order_repository: 注文データを取得するRepository。
            delivery_api_client: 最新の配送状況を取得するクライアント。
        """
        self.order_repository = order_repository
        self.delivery_api_client = delivery_api_client

    async def get_order(self, order_id: int) -> OrderResult | None:
        """注文を1件取得し、最新の配送状況を付加する。

        Args:
            order_id: 取得する注文の識別子。

        Returns:
            OrderResult | None: 注文が存在すれば配送状況付きの結果、なければNone。
        """
        order = self.order_repository.get_order(order_id)
        if order is None:
            return None

        delivery = await self.delivery_api_client.get_delivery_status(order.id)
        return self._to_result(order, delivery)

    async def list_orders(self, limit: int = 100) -> list[OrderResult]:
        """指定件数の注文を取得し、各注文の配送状況を付加する。

        Args:
            limit: 取得する注文の最大件数。

        Returns:
            list[OrderResult]: Repositoryの並び順を保った注文結果一覧。
        """
        orders = self.order_repository.list_orders(limit)
        result: list[OrderResult] = []
        for order in orders:
            delivery = await self.delivery_api_client.get_delivery_status(order.id)
            result.append(self._to_result(order, delivery))
        return result

    @staticmethod
    def _to_result(order: Order, delivery_status: str) -> OrderResult:
        """注文と配送状況をユースケース結果へ変換する。

        Args:
            order: 変換元のドメイン注文。
            delivery_status: 外部配送APIから取得した配送状況。

        Returns:
            OrderResult: 注文情報と配送状況をまとめた結果。
        """
        return OrderResult(
            order_id=order.id,
            customer_name=order.customer_name,
            delivery_status=delivery_status,
        )
