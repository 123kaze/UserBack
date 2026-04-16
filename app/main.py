from fastapi import FastAPI
from app.database import engine, Base
from app.routers import department, position, employee

# 启动时自动创建所有表（如果表不存在的话）
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(title="企业员工管理系统")

# 注册三个子路由，用 prefix 区分模块
app.include_router(department.router, prefix="/departments", tags=["部门管理"])
app.include_router(position.router, prefix="/positions", tags=["职位管理"])
app.include_router(employee.router, prefix="/employees", tags=["员工管理"])