import uvicorn
from fastapi import FastAPI , Path
app = FastAPI()
# @app.get("/")
# async def index():
#    return {"message": "Hello World"}
# @app.get("/hello/{name}/{age}/{city}")
# async def hello(name,age,city):
#    return {
#        "message": f"Hello {name}, you are {age} years old and lives in {city}."
#    }

# @app.get("/greet")
# async def greet(name: str = "Guest"):
#     return {"message": f"Hello, {name}!"}

@app.get("/hello/{name}")
async def hello(name:str=Path(...,
    title="Name",
    description="The name of the person to greet",
    min_length=3,
    max_length=10
)):
    return {"message": f"Hello, {name}!"}



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)