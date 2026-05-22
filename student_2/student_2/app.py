from fastapi import FastAPI, HTTPException,Depends,Request
from pydantic import BaseModel
from typing import Dict
import time

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Pydantic Model (Request Body)
# -------------------------------
class Student(BaseModel):
    name: str
    roll_no: int
    phone: str
    student_class: str


# -------------------------------
# In-memory database
# -------------------------------
students_db: Dict[int, Student] = {}


# -------------------------------
# Create Student (POST)
# -------------------------------
@app.post("/students")
async def create_student(student: Student, request: Request):

    if student.roll_no in students_db:
        raise HTTPException(status_code=400, detail="Roll number already exists")

    students_db[student.roll_no] = student

    data = str(request.url)
    ip=request.client.host   # ✅ no await

    return {
        "message": "Student created successfully",
        "data": student,
        "url": data,
        "ip":ip
    }


# -------------------------------
# Get Student by Roll (Path Param)
# -------------------------------
@app.get("/students/{roll_no}")
def get_student(roll_no: int,request:Request):
    student = students_db.get(roll_no)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "Student":student,
        "method":request.method,
        "params": request.json

    }


# -------------------------------
# Get Students by Class (Query Param)
# -------------------------------
@app.get("/student")
def get_students_by_class(student_class: str = None):
    if student_class:
        filtered_students = [
            student for student in students_db.values()
            if student.student_class == student_class
        ]
        return filtered_students

    return list(students_db.values())


# -------------------------------
# Update Student (PUT)
# -------------------------------
@app.put("/students/{roll_no}")
def update_student(roll_no: int, updated_student: Student):
    if roll_no not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")

    students_db[roll_no] = updated_student
    return {
        "message": "Student updated successfully",
        "data": updated_student
    }


# -------------------------------
# Delete Student (DELETE)
# -------------------------------
@app.delete("/students/{roll_no}")
def delete_student(roll_no: int):
    if roll_no not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")

    deleted_student = students_db.pop(roll_no)

    return {
        "message": "Student deleted successfully",
        "data": deleted_student
    }

def verify_token(token: str):
    if token != "secret":
        raise HTTPException(status_code=401, detail="Invalid token")
    return token
@app.get("/secure")
def secure_route(token: str = Depends(verify_token)):
    return {"message": "Access granted"}
def get_db():
    return "db connection"

def get_user(db = Depends(get_db)):
    return "user from db"

@app.get("/")
def root(user = Depends(get_user)):
    return user



@app.middleware("http")
async def log_request_time(request: Request, call_next):

    print("Before route execution")

    start_time = time.time()

    response = await call_next(request)  # Route runs here

    process_time = time.time() - start_time

    print("After route execution")
    print(f"Time taken: {process_time}")

    return response
