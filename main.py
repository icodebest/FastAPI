from fastapi import FastAPI, Path, HTTPException, Query
import json
import os

app = FastAPI()

def load_data():
    file_path = 'patient.json'
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="patient.json not found")
    
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
def view_patient(patient_id: str = Path(..., description='ID of the patient in DB', examples=['P001'])):
    data = load_data()

    # Fix: Check if data is a dict (not a list)
    if isinstance(data, dict):
        if patient_id in data:
            return data[patient_id]
    else:
        for patient in data:
            if patient.get("id") == patient_id:
                return patient

    raise HTTPException(status_code=404, detail='Patient Not Found')

@app.get('/sort')
def sort_patients(
    sort_by: str = Query(..., description='Sort by height, weight or bmi'),
    order: str = Query('asc', description='Sort in asc or desc order')
):
    valid_fields = ['height', 'weight', 'bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field. Choose from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order. Choose asc or desc')

    data = load_data()

    # Fix: Ensure sorting logic works correctly for both dict and list
    if isinstance(data, dict):
        data = list(data.values())

    reverse_sort = True if order == 'desc' else False
    sorted_data = sorted(data, key=lambda x: x.get(sort_by, 0), reverse=reverse_sort)

    return {"sorted": sorted_data}
    