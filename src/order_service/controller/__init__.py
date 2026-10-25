"""注文APIのルーターを公開する。"""

from .order_controller import create_order_router

__all__ = ["create_order_router"]
