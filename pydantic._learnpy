# BaseModel, Type Conversion, Easy access through object, Conditions, Pydantic predefined functions, Fields, Field-Validator, 
#Use of list, optional
from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator
from typing import List, Optional, Annotated
class Patient(BaseModel):
    # Field--> Custom data validation , Attatch meta data like in name, set a default value, type conversion
    name: Annotated[str, Field(max_length=50, title="Name of the Patient", description='Give the name of patient in less that 50 char', examples=['Waleed','Waleed Usman'])]
    email:EmailStr
    age: int= Field(gt=0, le=100)
    weight:float= Field(gt=0, lt=120)
    married: Annotated[bool, Field(default=None, description='Is the patient married or not')]
    allergies:Optional[List[str]]=None
    contact_detail:dict[str,str]


    # Field Validator for the Email.
    @field_validator('email')
    @classmethod
    def email_validator(cls, value):
        valid_domains=['nutech.edu.pk', 'NUTECH.EDU.PK']

        domain_name=value.split('@')[-1]

        if domain_name not in valid_domains:
            raise ValueError ('Not in valid domain')
        return value

    #Field Validator for Name Should be in Capital
    @field_validator('name')
    @classmethod
    def transform_name(cls,value):
        return value.upper()

    @field_validator('age',mode='after')
    @classmethod
    def validate_age(cls,value):
        if 0< value <100:
            return value
        else:
            raise ValueError('Age should be in between 0 and 100')


patient_info={'name':'Waleed','email':'waleed@nutech.edu.pk','age':'20','weight':'70','married':False, 'contact_detail':{'email':'abc@gamil.com', 'phone':'122312312'}}

patient1=Patient(**patient_info)

def insert_patient_data(patient: Patient):

    print(patient.name)
    print(patient.age)
    print(patient.allergies)
    print('Inserted')

insert_patient_data(patient1)