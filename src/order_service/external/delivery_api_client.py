"""配送APIとのHTTP通信を担当するクライアントを定義する。"""

import os

import httpx
from pydantic import BaseModel


class _DeliveryStatusResponse(BaseModel):
    """配送APIから返されるJSONレスポンスの形式。"""

    order_id: int
    status: str


class DeliveryApiClient:
    """配送APIへHTTPリクエストを送り、配送状況を取得する。"""

    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str | None = None,
    ) -> None:
        """共有HTTPクライアントと配送APIの接続先を設定する。

        Args:
            client: アプリケーションで共有する非同期HTTPクライアント。
            base_url: 配送APIのベースURL。省略時は環境変数または既定値を使う。
        """
        self.base_url = (
            base_url or os.getenv("DELIVERY_API_BASE_URL", "http://127.0.0.1:9000")
        ).rstrip("/")
        self.client = client

    async def get_delivery_status(self, order_id: int) -> str:
        """注文IDを指定して配送APIから最新状況を取得する。

        Args:
            order_id: 配送状況を照会する注文の識別子。

        Returns:
            str: 配送APIが返した配送状況。

        Raises:
            httpx.HTTPStatusError: 配送APIが成功以外のHTTPステータスを返した場合。
            httpx.RequestError: 通信またはタイムアウトに失敗した場合。
            pydantic.ValidationError: 配送APIのレスポンス形式が不正な場合。
        """
        response = await self.client.get(
            f"{self.base_url}/delivery-status/{order_id}"
        )
        response.raise_for_status()
        payload = _DeliveryStatusResponse.model_validate(response.json())
        return payload.status
