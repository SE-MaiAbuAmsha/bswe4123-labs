"""Lab 2 - a REST service that manages university courses."""
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

app = FastAPI(title="Courses Service")

class Course(BaseModel):
    code: str = Field(min_length=3, max_length=12, examples=["BSWE4321"])
    title: str = Field(min_length=3, examples=["Distributed Software Systems"])
    credits: int = Field(ge=1, le=6, examples=[2])
    capacity: int = Field(ge=1, examples=[40])

courses: dict[str, Course] = {}

@app.get("/courses")
def list_courses() -> list[Course]:
    return list(courses.values())

@app.get("/courses/{code}")
def get_course(code: str) -> Course:
    if code not in courses:
        raise HTTPException(status_code=404, detail=f"Course {code} not found")
    return courses[code]

@app.post("/courses", status_code=201)
def create_course(course: Course) -> Course:
    if course.code in courses:
        raise HTTPException(status_code=409, detail=f"Course {course.code} already exists")
    courses[course.code] = course
    return course

@app.put("/courses/{code}")
def replace_course(code: str, course: Course) -> Course:
    if course.code != code:
        raise HTTPException(status_code=400, detail="The code in the URL and in the body differ")
    courses[code] = course
    return course

@app.delete("/courses/{code}", status_code=204)
def delete_course(code: str) -> Response:
    if code not in courses:
        raise HTTPException(status_code=404, detail=f"Course {code} not found")
    del courses[code]
    return Response(status_code=204)

# Phase 2 Challenge: Enrollments 
class EnrollmentRequest(BaseModel):
    student_id: str = Field(min_length=5, examples=["120201234"])

enrollments: dict[str, list[str]] = {}

@app.post("/courses/{code}/enrollments", status_code=201)
def enroll_student(code: str, req: EnrollmentRequest):
    if code not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if code not in enrollments:
        enrollments[code] = []
        
    if req.student_id in enrollments[code]:
        raise HTTPException(status_code=409, detail="Student already enrolled")
        
    if len(enrollments[code]) >= courses[code].capacity:
        raise HTTPException(status_code=409, detail="Course is full")
        
    enrollments[code].append(req.student_id)
    return {"message": "Enrolled successfully", "student_id": req.student_id}

@app.get("/courses/{code}/enrollments")
def list_enrollments(code: str):
    if code not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"course": code, "enrolled_students": enrollments.get(code, [])}

@app.delete("/courses/{code}/enrollments/{student_id}", status_code=204)
def unenroll_student(code: str, student_id: str):
    if code not in courses or student_id not in enrollments.get(code, []):
        raise HTTPException(status_code=404, detail="Student not enrolled")
    
    enrollments[code].remove(student_id)
    return Response(status_code=204)