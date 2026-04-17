from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql.base import PGDialect

# OpenGauss 的版本字符串无法被 SQLAlchemy 识别，直接返回固定版本号
_original_get_server_version_info = PGDialect._get_server_version_info

def _patched_get_server_version_info(self, connection):
    try:
        return _original_get_server_version_info(self, connection)
    except AssertionError:
        # OpenGauss 兼容 PostgreSQL 9.2 协议
        return (9, 2, 4)

PGDialect._get_server_version_info = _patched_get_server_version_info

DATABASE_URL = "postgresql+psycopg2://kaze:Kaze%40654321@localhost:5432/employee_db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
 
 
def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()   # 打开数据库连接
    try:
        yield db          # 把连接交出去用
    finally:
        db.close()        # 用完自动关闭

