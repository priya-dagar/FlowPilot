from .database import SessionLocal
from .models import Employee

db = SessionLocal()


def get_or_create_employee(name, email, leave_balance=18, manager_id=None):
    employee = (
        db.query(Employee)
        .filter(Employee.email == email)
        .first()
    )

    if employee:
        return employee

    employee = Employee(
        name=name,
        email=email,
        leave_balance=leave_balance,
        manager_id=manager_id,
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


# Manager
manager = get_or_create_employee(
    name="Rahul Mehta",
    email="rahul@flowpilot.com",
    leave_balance=20,
)

# Employees
priya = get_or_create_employee(
    name="Priya Sharma",
    email="priya@flowpilot.com",
    leave_balance=18,
    manager_id=manager.id,
)

arjun = get_or_create_employee(
    name="Arjun Verma",
    email="arjun@flowpilot.com",
    leave_balance=15,
    manager_id=manager.id,
)

neha = get_or_create_employee(
    name="Neha Kapoor",
    email="neha@flowpilot.com",
    leave_balance=12,
    manager_id=manager.id,
)

rohan = get_or_create_employee(
    name="Rohan Singh",
    email="rohan@flowpilot.com",
    leave_balance=16,
    manager_id=manager.id,
)

ananya = get_or_create_employee(
    name="Ananya Gupta",
    email="ananya@flowpilot.com",
    leave_balance=14,
    manager_id=manager.id,
)

karan = get_or_create_employee(
    name="Karan Malhotra",
    email="karan@flowpilot.com",
    leave_balance=10,
    manager_id=manager.id,
)

print(f"Manager: {manager.name} (ID: {manager.id})")
print(f"Employee: {priya.name} (ID: {priya.id})")
print(f"Employee: {arjun.name} (ID: {arjun.id})")
print(f"Employee: {neha.name} (ID: {neha.id})")
print(f"Employee: {rohan.name} (ID: {rohan.id})")
print(f"Employee: {ananya.name} (ID: {ananya.id})")
print(f"Employee: {karan.name} (ID: {karan.id})")

db.close()