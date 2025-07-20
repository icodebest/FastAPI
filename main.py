from fastapi import FastAPI, Path, HTTPException
import json
import os

app = FastAPI()

def load_data():
    file_path = 'patient.json'
    if not os.path.exists(file_path):
        return {"error": "patient.json not found"}
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

@app.get("/")
def hello():
    return {"message": "Patient Management System API"}

@app.get("/about")
def about():
    return {"message": "A fully functional API for managing patient data"}

@app.get("/view")
def view():
    data = load_data()
    return {"data": data}


@app.get('/patient/{patient_id}')
def view_patient(patient_id: str=Path(..., description='ID of the patient in DB', example='P001')):
    #load all the patient data
    data=load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient Not Found')