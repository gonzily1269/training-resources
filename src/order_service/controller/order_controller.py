"""注文APIのHTTPルートとレスポンス変換を定義する。"""

from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from order_service.schema import OrderResponse
from order_service.service import OrderService


def create_order_router(
    get_order_service: Callable[..., OrderService],
) -> APIRouter:
    """注文ユースケースを呼び出すAPIルーターを生成する。

    Args:
        get_order_service: リクエストごとに注文サービスを提供する依存関数。

    Returns:
        APIRouter: 注文一覧・単数取得エンドポイントを持つルーター。
    """
    router = APIRouter()
    order_service_dependency = Annotated[
        OrderService,
        Depends(get_order_service),
    ]

    @router.get("/orders/{order_id}", response_model=OrderResponse)
    async def get_order(
        order_id: int,
        service: order_service_dependency,
    ) -> OrderResponse:
        """指定された注文と最新の配送状況を返す。

        Args:
            order_id: 取得する注文の識別子。
            service: 注文取得を実行するサービス。

        Returns:
            OrderResponse: 注文情報と配送状況。

        Raises:
            HTTPException: 注文が存在しない場合に404を返す。
        """
        order = await service.get_order(order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return OrderResponse(
            orderId=order.order_id,
            customerName=order.customer_name,
            deliveryStatus=order.delivery_status,
        )

    @router.get("/orders", response_model=list[OrderResponse])
    async def list_orders(
        service: order_service_dependency,
        limit: int = Query(default=100, ge=1, le=100),
    ) -> list[OrderResponse]:
        """更新日時の新しい順に注文と配送状況を返す。

        Args:
            service: 注文一覧取得を実行するサービス。
            limit: 取得する注文数（1〜100）。省略時は100件。

        Returns:
            list[OrderResponse]: 注文情報と配送状況の一覧。
        """
        orders = await service.list_orders(limit=limit)
        return [
            OrderResponse(
                orderId=order.order_id,
                customerName=order.customer_name,
                deliveryStatus=order.delivery_status,
            )
            for order in orders
        ]

    return router
