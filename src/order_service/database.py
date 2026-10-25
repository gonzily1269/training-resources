"""データベース接続とセッション管理を提供する。"""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """SQLAlchemyのORMモデルが継承する宣言的ベース。"""

DATABASE_PATH = Path(__file__).resolve().parents[2] / "order.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """リクエスト単位で使用するDBセッションを生成して解放する。

    Yields:
        Session: 呼び出し元が利用するSQLAlchemyセッション。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
