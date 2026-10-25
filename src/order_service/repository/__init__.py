"""注文データの永続化アダプターを公開する。"""

from .order_repository import OrderRecord, OrderRepository

__all__ = ["OrderRecord", "OrderRepository"]
