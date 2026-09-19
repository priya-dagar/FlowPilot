from .database import SessionLocal
from .models import Employee

db = SessionLocal()

manager = Employee(
    name="Rahul Mehta",
    email="rahul@flowpilot.com",
    leave_balance=20
)

db.add(manager)
db.commit()
db.refresh(manager)

employee = Employee(
    name="Priya Sharma",
    email="priya@flowpilot.com",
    manager_id=manager.id,
    leave_balance=18
)

db.add(employee)
db.commit()

print(f"Manager ID: {manager.id}")
print(f"Employee ID: {employee.id}")

db.close()