from pydantic import BaseModel, EmailStr, model_validator, computed_field
from typing import List, Optional, Dict

class Patient(BaseModel):
    name: str
    email: EmailStr
    age: int
    weight: float
    height:float
    married: bool
    allergies: Optional[List[str]] = None  # now optional
    contact_detail: Dict[str, str]

    @model_validator(mode='after')
    def validate_emergency_contact(cls, model):
        if model.age > 60 and 'emergency' not in model.contact_detail:
            raise ValueError('Patient older than 60 must have an emergency contact number')
        return model

    @computed_field
    @property
    def calculate_bmi(self)->float:
        bmi=round(self.weight/(self.height**2), 2)
        return bmi




patient_info = {
    'name': 'Waleed',
    'email': 'waleed@gmail.com',
    'age': '80',
    'weight': '70',
    'height':'5.3',
    'married': False,
    'contact_detail': {
        'email': 'abc@gamil.com',
        'phone': '122312312',
        'emergency':'23232323'
    },
    'allergies': ['dust']  # optional but added
}

patient1 = Patient(**patient_info)

def insert_patient_data(patient: Patient):
    print(patient.name)
    print(patient.age)
    print(patient.allergies)
    print('Bmi',patient.calculate_bmi )
    print('Inserted')

insert_patient_data(patient1)
