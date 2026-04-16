from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
 
DATABASE_URL = "postgresql+psycopg2://kaze:Kaze%40123456@localhost:5432/employee_db"
 
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

