from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Simple Todo API")

# Define the shape of our data
class TodoItem(BaseModel):
    id: int
    title: str
    completed: bool = False

# Sample data
todos = [
    TodoItem(id=1, title="Learn FastAPI", completed=False),
    TodoItem(id=2, title="Build a project", completed=False)
]

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


# Get all todos
@app.get("/todos", response_model=List[TodoItem])
def get_all_todos():
    return todos

# Get a specific todo
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

# Create a new todo
@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos.append(todo)
    return todo

# Update a todo
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: TodoItem):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            todos[index] = updated_todo
            return updated_todo
    raise HTTPException(status_code=404, detail="Todo not found")

# Delete a todo
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for index, todo in enumerate(todos):
        if todo.id == todo_id:
            todos.pop(index)
            return {"message": "Todo deleted successfully"}
    raise HTTPException(status_code=404, detail="Todo not found")