from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.EmployeeResponse])
def list_employees(
    name: str = None,
    department_id: int = None,
    position_id: int = None,
    db: Session = Depends(get_db),
):
    return crud.get_employee(db, name, department_id, position_id)


@router.get("/{employee_id}", response_model=schemas.EmployeeResponse)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = crud.get_employee_by_id(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    return emp


@router.post("/", response_model=schemas.EmployeeResponse, status_code=201)
def add_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return crud.create_employee(db, employee)


@router.put("/{employee_id}", response_model=schemas.EmployeeResponse)
def edit_employee(employee_id: int, employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    emp = crud.update_employee(db, employee_id, employee)
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    return emp


@router.delete("/{employee_id}")
def remove_employee(employee_id: int, db: Session = Depends(get_db)):
    if not crud.delete_employee(db, employee_id):
        raise HTTPException(status_code=404, detail="员工不存在")
    return {"detail": "删除成功"}
