#Benifits of Nested Models
#1. Better organization of related data
# Resuability: use of vitals in multiple models
# Readability: Easier for develloper to read and understand code
# Validation of the data


from pydantic import BaseModel

class Address(BaseModel):
    city:str
    state:str
    pin: str


class Patient(BaseModel):

    name:str
    gender:str
    age:int
    address:Address

address_dict={'city':'Rawalpindi', 'state':'Punjab','pin':'8004'}

address1=Address(**address_dict)

patient_dict={'name':'waleed', 'gender':'male', 'age':'20','address':address1}

patient1=Patient(**patient_dict)
print(patient1)
print(patient1.address.city)
print(patient1.address.state)
