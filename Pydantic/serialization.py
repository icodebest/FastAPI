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

#temp=patient1.model_dump(include=['name','age'])

#temp=patient1.model_dump(exclude=['name','age'])

temp=patient1.model_dump(exclude={'address':['state']})


print(temp)
print(type(temp))