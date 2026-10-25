"""Order Serviceのアプリケーション起動と依存関係を定義する。"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from time import perf_counter
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, Request
from sqlalchemy.orm import Session

from order_service.controller import create_order_router
from order_service.database import get_db
from order_service.external import DeliveryApiClient
from order_service.repository import OrderRepository
from order_service.service import OrderService

DatabaseSession = Annotated[Session, Depends(get_db)]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("order_service")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーション共有のHTTPクライアントを起動・終了時に管理する。

    Args:
        app: 起動するFastAPIアプリケーション。

    Yields:
        None: アプリケーションが稼働している期間。
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        app.state.delivery_http_client = client
        yield


def get_order_service(
    request: Request,
    db: DatabaseSession,
) -> OrderService:
    """DBセッションと共有HTTPクライアントから注文サービスを構築する。

    Args:
        request: HTTPリクエストとアプリケーション状態。
        db: このリクエストで使用するDBセッション。

    Returns:
        OrderService: 注文Repositoryと配送APIクライアントを組み合わせたサービス。
    """
    return OrderService(
        OrderRepository(db),
        DeliveryApiClient(request.app.state.delivery_http_client),
    )


app = FastAPI(title="Order Service", lifespan=lifespan)
app.include_router(create_order_router(get_order_service))


@app.middleware("http")
async def access_log(request, call_next):
    """HTTPリクエストの処理時間と結果をアクセスログに記録する。

    Args:
        request: 処理対象のHTTPリクエスト。
        call_next: 次のミドルウェアまたはルート処理を呼び出す関数。

    Returns:
        Response: 下流の処理が生成したHTTPレスポンス。
    """
    started = perf_counter()
    response = await call_next(request)
    logger.info(
        "%s %s %s %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        (perf_counter() - started) * 1000,
    )
    return response
