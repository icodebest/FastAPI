from fastapi import FastAPI
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
