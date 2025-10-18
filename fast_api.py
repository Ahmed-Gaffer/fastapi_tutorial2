from fastapi import FastAPI
from pydantic import BaseModel , Field
from fastapi import HTTPException
import json
import os

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يمكنك تحديد الأصول المسموح بها هنا
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تعريف نموذج الطالب مع التحقق من البيانات
class Student(BaseModel):
    id: int = Field(..., ge=1, description="Student ID must be >= 1")
    name: str = Field(..., min_length=1, description="Name cannot be empty")
    grade: int = Field(..., ge=0, le=100, description="Grade must be between 0 and 100")

if os.path.exists("students.json"):
    with open("students.json", "r", encoding="utf-8") as f:
        student_data = json.load(f)
        students = [Student(**s)for s in student_data]
else:
    students = []

@app.get("/students/")
def read_students():
    return students

@app.post("/students/", )
def create_student(new_student: Student):
    for student in students:
        if student.id == new_student.id:
           raise HTTPException(status_code=400, detail="Student with this ID already exists")
    students.append(new_student)
    with open("students.json", "w", encoding="utf-8") as f:
        json.dump([s.dict() for s in students], f, ensure_ascii=False, indent=4)
    return {"message": "Student created successfully", "student": new_student}

@app.put("/students/{student_id}")
def update_student(student_id: int, updated_student: Student):
    for index, student in enumerate(students):
        if student.id == student_id:
            students[index] = updated_student
            with open("students.json", "w", encoding="utf-8") as f:
                json.dump([s.dict() for s in students], f, ensure_ascii=False, indent=4)
            return {"message": "Student updated successfully", "student": updated_student}
    return {"error": "Student not found"}

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    for student in students:
        if student.id == student_id:
            students.remove(student)
            with open ("students.json", "w", encoding="utf-8") as f:
                json.dump([s.dict() for s in students], f, ensure_ascii=False, indent=4)
            return {"message": "Student deleted successfully"}
    return {"error": "Student with this ID was not found"}

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

