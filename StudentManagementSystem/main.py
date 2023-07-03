from fastapi import FastAPI, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
import pydantic
from bson import ObjectId

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

from schemas import StudentCreateRequest, StudentUpdateRequest
from database import student_collection

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Welcome to this fantastic Student Management !"}


@app.post("/student", status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreateRequest):
    student = jsonable_encoder(student)
    new_student = await student_collection.insert_one(student)
    created_student = await student_collection.find_one({"_id": new_student.inserted_id})
    return created_student


@app.put("/student/{studentId}", status_code=status.HTTP_200_OK)
async def update_student_by_id(studentId: str, student: StudentUpdateRequest):
    student = jsonable_encoder(student)
    isStudentValid = await student_collection.find_one({"_id": ObjectId(studentId)})
    if isStudentValid:
        updated_student = await student_collection.update_one({"_id": ObjectId(studentId)},
                                                              {"$set": student})
        if updated_student is not None and updated_student.acknowledged:
            updated_student = await student_collection.find_one({"_id": ObjectId(studentId)})
            return updated_student
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No student exists with Student Id {studentId}.")


@app.get("/student", status_code=status.HTTP_200_OK)
async def get_all_students():
    cursor = student_collection.find({})
    students = list()
    async for document in cursor:
        students.append(document)
    return students


@app.delete("/student/{studentId}", status_code=status.HTTP_200_OK)
async def delete_student_by_id(studentid: str):
    isStudentValid = await student_collection.find_one({"_id": ObjectId(studentid)})
    if isStudentValid:
        deleted_student = await student_collection.delete_one({"_id": ObjectId(studentid)})
        if deleted_student is not None and deleted_student.acknowledged:
            return {"detail": f"Student deleted successfully with student id {studentid}."}
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No student exists with Student Id {studentid}.")


@app.get("/student/{studentId}", status_code=status.HTTP_200_OK)
async def get_student_by_id(studentid: str):
    fetchedstudent = await student_collection.find_one({"_id": ObjectId(studentid)})
    if fetchedstudent:
        return fetchedstudent
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No student exists with Student Id {studentid}.")
