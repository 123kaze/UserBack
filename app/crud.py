from sqlalchemy.orm import Session
from app import models, schemas

# 查询所有部门
def get_departments(db: Session):
    return db.query(models.Department).all()

def get_department(db: Session,department_id: int): 
    '''
    查询单个部门
    '''
    return db.query(models.Department).filter(models.Department.id == department_id).first()



def create_department(db: Session,department:schemas.DepartmentCreate):
    '''
    创建部门
    '''
    db_dept = models.Department(**department.model_dump())
    # 用model.dump()把Pydantic对象换成字典
    # 然后用**解包成关键字参数传给Department构造函数
    db.add(db_dept)       # 1. 加入会话（相当于准备好 INSERT 语句）
    db.commit()           # 2. 提交事务（真正写入数据库）
    db.refresh(db_dept)   # 3. 刷新对象（从数据库拿回自动生成的 id、created_at）
    return db_dept        # 4. 返回完整对象

def update_department(db: Session, department_id: int, department: schemas.DepartmentCreate):
    '''
    更新部门
    '''
    db_dept = db.query(models.Department).filter(
        models.Department.id == department_id
    ).first()
    if not db_dept:
        return None
    for k,v in department.model_dump().items():
        setattr(db_dept, k, v)
    db.commit()
    db.refresh(db_dept)
    return db_dept

def delete_department(db: Session, department_id: int):
    '''
    删除部门
    '''
    db_dept = db.query(models.Department).filter(
        models.Department.id == department_id
    ).first()
    if not db_dept:
        return False
    db.delete(db_dept)
    db.commit()
    return True
    # TODO: 检查是否有用户属于该部门，如果有则不能删除
    # TODO: 检查是否有子部门，如果有则不能删除
    # TODO: 检查是否有角色属于该部门，如果有则不能删除
    # TODO: 检查是否有权限属于该部门，如果有则不能删除
    # TODO: 记得做一个认证服务，防止未授权访问

def get_positions(db: Session):
    '''
    查询所有职位
    '''
    return db.query(models.Position).all()

def get_position(db: Session, position_id: int):
    '''
    查询单个职位
    '''
    return db.query(models.Position).filter(models.Position.id == position_id).first()

def create_position(db: Session, position: schemas.PositionCreate):
    '''
    创建职位
    '''
    db_position = models.Position(**position.model_dump())
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position
    
def update_position(db: Session, position_id: int, position: schemas.PositionCreate):
    '''
    更新职位
    '''
    db_position = db.query(models.Position).filter(models.Position.id == position_id).first()
    if not db_position:
        return None
    for k,v in position.model_dump().items():
        setattr(db_position, k, v)
    db.commit()
    db.refresh(db_position)
    return db_position

def delete_position(db: Session, position_id: int):
    '''
    删除职位
    '''
    db_position = db.query(models.Position).filter(models.Position.id == position_id).first()
    if not db_position:
        return False
    db.delete(db_position)
    db.commit()
    return True

def get_employees(db: Session):
    '''
    查询所有员工
    '''
    return db.query(models.Employee).all()

def get_employee(db: Session,name:str = None,department_id:int = None,position_id:int = None):
    '''
    查询员工
    '''
    query = db.query(models.Employee)
    if position_id:
        query = query.filter(models.Employee.position_id == position_id)
    if department_id:
        query = query.filter(models.Employee.department_id == department_id)
    if name:
        query = query.filter(models.Employee.name.like(f'%{name}%'))
    return query.all()

def get_employee_by_id(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    '''
    创建员工
    '''
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db: Session, employee_id: int, employee: schemas.EmployeeCreate):
    '''
    更新员工
    '''
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        return None
    for k,v in employee.model_dump().items():
        setattr(db_employee, k, v)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def delete_employee(db: Session, employee_id: int):
    '''
    删除员工
    '''
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        return False
    db.delete(db_employee)
    db.commit()
    return True



