from fastapi import FastAPI, Path, HTTPException, Query, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Dict, Optional
import json
import os

app = FastAPI(
    title="Patient Management API",
    description="This version uses form input with full validation and Swagger UI field-wise inputs.",
    version="1.0.1"
)

# ------------------ Patient Model ------------------

class Patient(BaseModel):
    id: Annotated[str, Field(..., description='ID of the Patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the Patient')]
    city: Annotated[str, Field(..., description='City of the Patient')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the Patient')]
    gender: Annotated[Literal['male', 'female', 'other'], Field(..., description='Gender of the Patient')]
    height: Annotated[float, Field(..., gt=0, description='Height in meters')]
    weight: Annotated[float, Field(..., gt=0, description='Weight in kilograms')]

    # Computed BMI field
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    # Computed BMI verdict field
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'


# ------------------ Patient Update Model ------------------

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female', 'other']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


# ------------------ File Utility Functions ------------------

def load_data() -> Dict:
    """
    Load patient data from 'patient.json' file.
    """
    if not os.path.exists('patient.json'):
        return {}
    try:
        with open('patient.json', 'r') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}

def save_data(data: Dict):
    """
    Save the patient data back to 'patient.json'.
    """
    with open('patient.json', 'w') as f:
        json.dump(data, f, indent=4)


# ------------------ API Endpoints ------------------

@app.get("/")
def hello():
    return {"message": "Patient Management System API"}

@app.get("/about")
def about():
    return {"message": "A fully functional API for managing patient data"}

@app.get("/view")
def view_all_patients():
    """
    View all patients in the database.
    """
    data = load_data()
    return {"data": data}

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description='ID of the patient', examples=['P001'])):
    """
    View a specific patient by ID.
    """
    data = load_data()
    patient = data.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail='Patient Not Found')
    return patient

@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description='Sort by "height", "weight", or "bmi"'),
    order: str = Query('asc', description='Sort order: "asc" or "desc"')
):
    """
    Sort patients by height, weight, or BMI.
    """
    valid_fields = ['height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field. Choose from {valid_fields}')

    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order. Use "asc" or "desc"')

    data = load_data()
    patients = list(data.values())

    # Calculate BMI if sorting by it
    if sort_by == 'bmi':
        for p in patients:
            p['bmi'] = round(p['weight'] / (p['height'] ** 2), 2)

    sorted_data = sorted(patients, key=lambda x: x.get(sort_by, 0), reverse=(order == 'desc'))
    return {"sorted": sorted_data}

@app.post("/create")
def create_patient(patient: Patient):
    """
    Add a new patient to the database.
    """
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # Save patient using their ID as key
    data[patient.id] = patient.model_dump(exclude=['id'])
    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Patient Created Successfully"})

@app.put("/edit_patient/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
    """
    Update patient data by ID.
    """
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    existing_data = data[patient_id]

    # Merge new values into the existing patient info
    update_fields = patient_update.model_dump(exclude_unset=True)
    existing_data.update(update_fields)

    # Validate and recalculate BMI & verdict using Patient model
    existing_data['id'] = patient_id
    updated_patient = Patient(**existing_data)
    final_data = updated_patient.model_dump(exclude=['id'])

    data[patient_id] = final_data
    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'Patient Updated Successfully'})
