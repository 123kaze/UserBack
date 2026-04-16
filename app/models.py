from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
 
from app.database import Base
 
 
class Department(Base):
    __tablename__ = "departments"
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, comment="部门名称")
    description = Column(Text, nullable=True, comment="部门描述")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
 
    employees = relationship("Employee", back_populates="department")
 
 
class Position(Base):
    __tablename__ = "positions"
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False, unique=True, comment="职位名称")
    description = Column(Text, nullable=True, comment="职位描述")
    min_salary = Column(Numeric(10, 2), nullable=True, comment="最低薪资")
    max_salary = Column(Numeric(10, 2), nullable=True, comment="最高薪资")
 
    employees = relationship("Employee", back_populates="position")
 
 
class Employee(Base):
    __tablename__ = "employees"
 
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(String(10), nullable=True, comment="性别")
    birth_date = Column(Date, nullable=True, comment="出生日期")
    phone = Column(String(20), nullable=True, comment="手机号")
    email = Column(String(100), nullable=True, comment="邮箱")
    hire_date = Column(Date, nullable=True, comment="入职日期")
    salary = Column(Numeric(10, 2), nullable=True, comment="薪资")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="部门ID")
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True, comment="职位ID")
 
    department = relationship("Department", back_populates="employees")
    position = relationship("Position", back_populates="employees")
 

