# Order Service の起動手順

このプロジェクトでは、Python 3.12 以上と [uv](https://docs.astral.sh/uv/) を使います。

## 1. 環境を準備する

依存関係をインストールします。

```bash
uv sync
```

## 2. 初期データを入れる

サンプルの注文データを登録します。

```bash
uv run python scripts/seed.py
```

## 3. 配送API Mock を起動する

Order Service を起動する前に、配送状況を返す Mock API を別のターミナルで起動してください。

```bash
uv run python scripts/mock_delivery_api.py
```

Mock API は次の URL で起動します。

```text
http://127.0.0.1:9000
```

利用できるエンドポイントは次のとおりです。

```text
GET /delivery-status/{order_id}
```

動作確認例:

```bash
curl http://127.0.0.1:9000/delivery-status/1
# {"order_id":1,"status":"delivered"}
```

## 4. Order Service を起動する

次に、Order Service を別のターミナルで起動します。

```bash
uv run uvicorn order_service.main:app --reload
```

Order Service は次の URL で利用できます。

```text
http://127.0.0.1:8000
```

## 5. API を確認する

### 注文一覧を取得する

```bash
curl http://127.0.0.1:8000/orders
```

件数を絞り込む場合は `limit` を使います（1〜100件まで）。

```bash
curl http://127.0.0.1:8000/orders?limit=20
```

### 注文を1件取得する

```bash
curl http://127.0.0.1:8000/orders/1
```

## 開発環境

- Python 3.12+
- FastAPI
- SQLAlchemy
- SQLite
- uv

詳細な要件や設計書は `docs/` 配下を参照してください。
