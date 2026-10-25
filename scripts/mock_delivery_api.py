"""ローカル開発で使用する配送APIモックを提供する。"""

import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Delivery API Mock")

MAX_CONCURRENCY = 10
_current_requests = 0
_counter_lock = asyncio.Lock()


@app.get("/delivery-status/{order_id}", response_model=None)
async def get_delivery_status(order_id: int) -> dict[str, object] | JSONResponse:
    """注文の配送状況を返し、同時実行上限を超えた場合は429を返す。

    Args:
        order_id: 配送状況を照会する注文の識別子。

    Returns:
        dict[str, object] | JSONResponse: 配送状況、または同時実行超過エラー。
    """
    global _current_requests

    async with _counter_lock:
        if _current_requests >= MAX_CONCURRENCY:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "too_many_requests",
                    "message": "concurrency limit exceeded",
                },
            )
        _current_requests += 1

    try:
        await asyncio.sleep(1)
        # 動作確認用として、常に "delivered" を返すようにしている。
        return {"order_id": order_id, "status": "delivered"}
    finally:
        async with _counter_lock:
            _current_requests -= 1


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
