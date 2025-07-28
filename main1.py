from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, computed_field
from typing import Annotated, Literal, Dict, Optional
import json
import os

# -------------------- FastAPI App Initialization --------------------
app = FastAPI(
    title="Patient Management API",
    description="This version includes authentication and full patient management.",
    version="1.0.2"
)

# -------------------- Patient Data Model --------------------
class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of the Patient", examples=["P001"])]
    name: Annotated[str, Field(..., description="Name of the Patient")]
    city: Annotated[str, Field(..., description="City of the Patient")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age between 1 and 119")]
    gender: Annotated[Literal["male", "female", "other"], Field(..., description="Gender")]
    height: Annotated[float, Field(..., gt=0, description="Height in meters")]
    weight: Annotated[float, Field(..., gt=0, description="Weight in kilograms")]

    # Computed BMI field
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    # Computed verdict based on BMI
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

# -------------------- Patient Update Model --------------------
class PatientUpdate(BaseModel):
    name: Optional[str]
    city: Optional[str]
    age: Annotated[Optional[int], Field(gt=0)] = None
    gender: Optional[Literal["male", "female", "other"]]
    height: Annotated[Optional[float], Field(gt=0)] = None
    weight: Annotated[Optional[float], Field(gt=0)] = None

# -------------------- Signup Model --------------------
class SignUpForm(BaseModel):
    name: Annotated[str, Field(..., min_length=2)]
    email: EmailStr
    passward: Annotated[str, Field(..., min_length=6, description="Password must be at least 6 characters")]
    city: str
    age: Annotated[int, Field(gt=0)]
    gender: Literal["male", "female", "other"]
    height: Annotated[float, Field(gt=0)]
    weight: Annotated[float, Field(gt=0)]

# -------------------- Login Model --------------------
class LoginForm(BaseModel):
    email: EmailStr
    passward: Annotated[str, Field(..., min_length=6)]

# -------------------- File Utility Functions --------------------
def load_data() -> Dict:
    """Load patient data from patient.json"""
    if not os.path.exists("patient.json"):
        return {}
    try:
        with open("patient.json", "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}

def save_data(data: Dict):
    """Save patient data to patient.json"""
    with open("patient.json", "w") as f:
        json.dump(data, f, indent=4)

def load_users() -> Dict:
    """Load user credentials from users.json"""
    if not os.path.exists("users.json"):
        return {}
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}

def save_users(data: Dict):
    """Save user credentials to users.json"""
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

def generate_patient_id(existing_users: Dict) -> str:
    """Generate new patient ID like P001, P002"""
    if not existing_users:
        return "P001"
    ids = [int(uid[1:]) for uid in existing_users.keys() if uid.startswith("P")]
    new_id = max(ids) + 1 if ids else 1
    return f"P{new_id:03d}"

# -------------------- API Endpoints --------------------

@app.get("/")
def hello():
    return {"message": "Welcome to the Patient Management System API"}

@app.get("/about")
def about():
    return {"message": "API to manage patients with login/signup system"}

@app.get("/view")
def view_all_patients():
    """Returns all patients"""
    return {"data": load_data()}

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="ID like P001")):
    """Returns data for a specific patient by ID"""
    patients = load_data()
    patient = patients.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description='Sort by "height", "weight", or "bmi"'),
    order: str = Query("asc", description='Sort order: "asc" or "desc"')
):
    """Sort patients by height, weight or BMI"""
    valid_fields = ["height", "weight", "bmi"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by field: {sort_by}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Order must be 'asc' or 'desc'")

    patients = list(load_data().values())
    if sort_by == "bmi":
        for p in patients:
            p["bmi"] = round(p["weight"] / (p["height"] ** 2), 2)

    sorted_data = sorted(patients, key=lambda x: x.get(sort_by, 0), reverse=(order == "desc"))
    return {"sorted": sorted_data}

@app.post("/create")
def create_patient(patient: Patient):
    """Create a new patient (admin route)"""
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")
    data[patient.id] = patient.model_dump(exclude=["id"])
    save_data(data)
    return {"message": "Patient Created Successfully"}

@app.put("/edit_patient/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
    """Update patient by ID"""
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    current = data[patient_id]
    updates = patient_update.model_dump(exclude_unset=True)
    current.update(updates)

    current["id"] = patient_id
    updated = Patient(**current)
    data[patient_id] = updated.model_dump(exclude=["id"])
    save_data(data)

    return {"message": "Patient Updated Successfully"}

@app.delete("/delete_patient/{patient_id}")
def delete_patient(patient_id: str):
    """Delete patient by ID"""
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    del data[patient_id]
    save_data(data)
    return {"message": "Patient Deleted Successfully"}

# -------------------- Authentication --------------------

@app.post("/signup")
def signup(user: SignUpForm):
    """Signup user and auto-create patient profile"""
    users = load_users()

    # Check for duplicate email
    if any(u.get("email") == user.email for u in users.values()):
        raise HTTPException(status_code=400, detail="Email already registered")

    patient_id = generate_patient_id(users)

    # Create patient record
    patient_obj = Patient(
        id=patient_id,
        name=user.name,
        city=user.city,
        age=user.age,
        gender=user.gender,
        height=user.height,
        weight=user.weight
    )

    # Save to patient.json
    patients = load_data()
    patients[patient_id] = patient_obj.model_dump(exclude=["id"])
    save_data(patients)

    # Save user credentials to users.json
    users[patient_id] = {
        "id": patient_id,
        "name": user.name,
        "email": user.email,
        "passward": user.passward  # In production, hash this!
    }
    save_users(users)

    return {
        "message": "Signup successful!",
        "patient_id": patient_id,
        "patient_record": patient_obj
    }

@app.post("/login")
def login(credentials: LoginForm):
    """Login using email and password"""
    users = load_users()
    for uid, user in users.items():
        if user["email"] == credentials.email and user["passward"] == credentials.passward:
            return {
                "message": "Login successful!",
                "patient_id": uid,
                "name": user["name"]
            }
    raise HTTPException(status_code=401, detail="Invalid email or password")
