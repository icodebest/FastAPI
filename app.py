from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Literal, Annotated
import pickle
import pandas as pd


#import the model
with open('model.pkl', 'rb') as f:
    model=pickle.load(f)


app=FastAPI()


tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]

#pydantic model to valuidate incoming data
class UserInput(BaseModel):

    age:Annotated[int, Field(..., gt=0, lt=120, description='Age of the User')]
    weight:Annotated[float, Field(..., gt=0, description='Weight of the User')]
    height:Annotated[float, Field(..., gt=0, lt=2.5, description='Height of the User')]
    income_lpa:Annotated[float, Field(..., gt=0, description='Income of the User in Lakhs Per Annum')]
    smoker:Annotated[bool, Field(..., description='Is the User a Smoker')]
    city:Annotated[str, Field(..., description='City of the User')]
    occupation:Annotated[Literal['retired','freelancer', 'student','government_job','business_owner','unemployed','private_job'], 
                         Field(..., description='Occupation of the User')]

    @computed_field
    @property
    def bmi(self)-> float:
        return self.weight / (self.height ** 2)
    

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker and self.bmi > 25:
            return "medium"
        else:
            return "low"
    
    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 18:
            return "young"
        elif self.age < 45:
            return "adult"
        else:
            return "senior"

    @computed_field
    @property
    def city_tier(self) -> str:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3


@app.post("/predict")
async def predict(data: UserInput):
    print("Received data:", data.dict())  # Debug log to print the received data
    # Convert the input data to a DataFrame
    input_data = pd.DataFrame([{
        "age": data.age,
        "weight": data.weight,
        "height": data.height,
        "income_lpa": data.income_lpa,
        "smoker": int(data.smoker),  # Convert boolean to int
        "city_tier": data.city_tier,
        "occupation": data.occupation,
        "bmi": data.bmi,
        "lifestyle_risk": data.lifestyle_risk,
        "age_group": data.age_group
    }])
    
    # Make predictions using the loaded model
    prediction = model.predict(input_data)
    
    # Return the prediction result
    return JSONResponse(content={"insurance_premium_category": prediction[0]})