from fastapi import FastAPI

# Create the FastAPI app instance
app = FastAPI()

# Create a simple greeting endpoint
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

# Create an endpoint that takes a name parameter
@app.get("/greet/{name}")
def greet_user(name: str):
    return {"message": f"Hello, {name}! Welcome to FastAPI."}

# Create an endpoint with optional query parameter
@app.get("/calculate")
def calculate_double(number: int):
    result = number * 2
    return {
        "original_number": number,
        "doubled_value": result,
        "message": f"Double of {number} is {result}"
    }