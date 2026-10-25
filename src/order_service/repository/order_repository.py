"""SQLAlchemyを使った注文データの永続化を担当する。"""

from datetime import UTC, datetime

from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from order_service.database import Base
from order_service.model import Order


class OrderRecord(Base):
    """SQLiteのordersテーブルに対応するORMレコード。"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    update_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class OrderRepository:
    """注文レコードの読み出しとドメインモデルへの変換を行う。"""

    def __init__(self, db: Session) -> None:
        """利用するSQLAlchemyセッションを設定する。

        Args:
            db: 注文の読み出しに使用するDBセッション。
        """
        self.db = db

    def get_order(self, order_id: int) -> Order | None:
        """識別子で注文を1件検索する。

        Args:
            order_id: 検索する注文の識別子。

        Returns:
            Order | None: 注文が存在すればドメインモデル、なければNone。
        """
        record = self.db.get(OrderRecord, order_id)
        return self._to_domain(record) if record is not None else None

    def list_orders(self, limit: int = 100) -> list[Order]:
        """更新日時と注文IDの降順で注文を取得する。

        Args:
            limit: 取得する注文の最大件数。

        Returns:
            list[Order]: 並び順を適用したドメイン注文の一覧。
        """
        records = self.db.scalars(
            select(OrderRecord)
            .order_by(OrderRecord.update_at.desc(), OrderRecord.id.desc())
            .limit(limit)
        ).all()
        return [self._to_domain(record) for record in records]

    @staticmethod
    def _to_domain(record: OrderRecord) -> Order:
        """ORMレコードをDB非依存のドメインモデルへ変換する。

        Args:
            record: 変換元のSQLAlchemy注文レコード。

        Returns:
            Order: ドメイン層で扱う注文。
        """
        return Order(
            id=record.id,
            customer_name=record.customer_name,
            update_at=record.update_at,
        )
